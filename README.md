# Retail Analytics Copilot

A local AI agent for retail analytics using RAG + SQL + DSPy.

## Overview
This agent answers questions about Northwind database and local policy documents.
It uses:
- **LangGraph** for orchestration (Router -> RAG/SQL -> Synthesizer).
- **DSPy** for prompt optimization (specifically the NL->SQL generation).
- **SQLite** for data storage.
- **TF-IDF** for document retrieval.
- **Ollama (Phi-3.5)** for local inference.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure Ollama is running with `phi3.5:3.8b-mini-instruct-q4_K_M`.
3. Run the agent:
   ```bash
   python run_agent_hybrid.py --batch sample_questions_hybrid_eval.jsonl --out outputs_hybrid.jsonl
   ```

## Design
- **Router**: Classifies questions as RAG, SQL, or Hybrid.
- **Retriever**: Fetches relevant chunks from `docs/`.
- **Planner**: Extracts constraints (dates, categories).
- **SQL Generator**: DSPy module optimized with BootstrapFewShot to generate valid SQL.
- **Executor**: Runs SQL against Northwind DB.
- **Synthesizer**: Combines results and generates formatted answer with citations.
- **Repair Loop**: Retries SQL generation if execution fails.

## Optimization
The `GenerateSQL` module was optimized using `BootstrapFewShot` with a small training set (`agent/train_data.py`).
- **Metric**: SQL validity (starts with SELECT).
- **Improvement**: The optimizer selects better few-shot examples to ensure valid SQL generation for complex queries (e.g., joins, aggregations).

## Assumptions
- CostOfGoods is approximated as 0.7 * UnitPrice if not available.
- Dates in marketing calendar are strict boundaries.