# Retail Analytics Copilot

A local AI agent for retail analytics using RAG + SQL + DSPy optimization.

## Overview
This agent answers questions about the Northwind database and local policy documents using:
- **LangGraph** for orchestration (7 nodes + repair loop)
- **DSPy** for prompt optimization (NL→SQL generation)
- **SQLite** (Northwind database)
- **TF-IDF** for document retrieval
- **Ollama (Phi-3.5-mini)** for local inference (no external API calls)

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure Ollama is running with `phi3.5:3.8b-mini-instruct-q4_K_M`:
   ```bash
   ollama pull phi3.5:3.8b-mini-instruct-q4_K_M
   ```
3. Run the agent:
   ```bash
   python run_agent_hybrid.py --batch sample_questions_hybrid_eval.jsonl --out outputs_hybrid.jsonl
   ```

## Graph Design
The LangGraph agent has **7 nodes** with a repair loop:
1. **Router**: Classifies questions as `rag`, `sql`, or `hybrid` using DSPy
2. **Retriever**: TF-IDF search over `docs/` (returns top-k chunks with IDs)
3. **Planner**: Extracts constraints (dates, categories, KPI formulas) from retrieved docs
4. **SQL Generator**: DSPy-optimized module that generates SQLite queries using schema introspection
5. **Executor**: Runs SQL against Northwind database
6. **Synthesizer**: Combines SQL results + retrieved docs to produce typed answers with citations
7. **Repair Loop**: Retries SQL generation up to 2 times on execution errors

## DSPy Optimization
**Module**: `GenerateSQL` (NL→SQL conversion)  
**Optimizer**: `BootstrapFewShot`  
**Training Data**: 7 verified SQL examples (all tested against live database)  
**Metric**: SQL validity and executability  

Run `python test_queries.py` to verify all training SQL queries work correctly.

## Evaluation Results

| Question | Type | Status | Result |
|----------|------|--------|--------|
| rag_policy_beverages_return_days | RAG |  Pass | 14 days |
| hybrid_top_category_qty_summer_1997 | Hybrid |  Partial | Incorrect SQL |
| hybrid_aov_winter_1997 | Hybrid |  Failed | SQL generation error |
| sql_top3_products_by_revenue_alltime | SQL |  Failed | SQL generation error |
| hybrid_revenue_beverages_summer_1997 | Hybrid |  Partial | Returns 0.00 |
| hybrid_best_customer_margin_1997 | Hybrid |  Failed | SQL generation error |

**Success Rate**: 16.7% (1/6 fully working, 2/6 partial)

## Current Limitations

### 1. SQL Generation Accuracy (~17% success)
**Problem**: The Phi-3.5-mini model (3.8B parameters) struggles with complex SQL queries.

**Root Causes**:
- Model too small for reliable SQL generation
- Difficulty with multi-table joins
- Poor handling of date filtering in SQLite syntax
- Cannot maintain context for nested subqueries

**Evidence**:
-  RAG-only questions: 100% success
-  Complex SQL/Hybrid: 0-17% success
-  Training queries: 100% execute correctly
-  Generated queries: Mostly fail or return wrong results

### 2. Specific SQL Issues
- **Date Filtering**: Model generates invalid SQLite date syntax
- **Join Complexity**: Fails on 3+ table joins
- **Aggregations**: Incorrect GROUP BY and window functions
- **Schema Understanding**: Doesn't reliably use correct table/column names

## Solutions & Recommendations

### Option 1: Use Larger Local Models
**Models to try**:
- **Llama 3 8B-70B** - Better SQL generation
- **CodeLlama 13B-34B** - Strong SQL capabilities
- **Mixtral 8x7B** - Good balance of size and performance

**Expected Improvement**: 50-80% success rate with 8B+ models

### Option 2: Fine-tune on SQL Dataset
**Approach**: Fine-tune Phi-3.5 on SQL-specific dataset
- Fine-tune with LoRA/QLoRA for efficiency
- Focus on SQLite-specific syntax

**Expected Improvement**: 40-60% success rate

## Assumptions
- **CostOfGoods**: Approximated as `0.7 * UnitPrice` when not available
- **Date Filtering**: Marketing calendar dates are strict boundaries (inclusive)
- **Categories**: Mapped via `Products.CategoryID` joins

## Project Structure
```
your_project/
├── agent/
│   ├── graph_hybrid.py          # LangGraph orchestration
│   ├── dspy_signatures.py       # DSPy signatures
│   ├── rag/retrieval.py         # TF-IDF retriever
│   ├── tools/sqlite_tool.py     # SQLite executor
│   └── train_data.py            # 7 verified training examples
├── data/northwind.sqlite        # Northwind database
├── docs/                        # Policy and KPI documents
├── run_agent_hybrid.py          # CLI entrypoint
└── test_queries.py              # Verify training SQL queries
```

## Output Contract
Each answer in `outputs_hybrid.jsonl` contains:
- `id`: Question identifier
- `final_answer`: Typed answer matching format_hint (int/float/list/object)
- `sql`: Last executed SQL query (empty for RAG-only)
- `confidence`: 0.0-1.0 heuristic based on retrieval + SQL success
- `explanation`: Brief justification (≤2 sentences)
- `citations`: Database tables + document chunk IDs used