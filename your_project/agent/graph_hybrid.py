import dspy
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from your_project.agent.dspy_signatures import Router, Planner, GenerateSQL, SynthesizeAnswer
from your_project.agent.rag.retrieval import Retriever
from your_project.agent.tools.sqlite_tool import SQLiteTool
import os

class AgentState(TypedDict):
    question: str
    classification: str
    retrieved_docs: List[Dict[str, Any]]
    constraints: str
    sql_query: str
    sql_result: Dict[str, Any]
    final_answer: Any
    explanation: str
    citations: List[str]
    error: Optional[str]
    repair_count: int
    format_hint: str

class RetailAgent:
    def __init__(self, db_path, docs_dir):
        self.retriever = Retriever(docs_dir)
        self.sqlite_tool = SQLiteTool(db_path)
        self.schema = self.sqlite_tool.get_schema()
        
        # DSPy Modules
        self.router_module = dspy.Predict(Router)
        self.planner_module = dspy.ChainOfThought(Planner)
        
        # Load compiled SQL generator if available
        compiled_sql_path = 'your_project/agent/compiled_sql_generator.json'
        if os.path.exists(compiled_sql_path):
            # We need to define the class structure to load it
            class SQLGenerator(dspy.Module):
                def __init__(self):
                    super().__init__()
                    self.generate = dspy.ChainOfThought(GenerateSQL)
                def forward(self, question, schema, constraints):
                    return self.generate(question=question, schema=schema, constraints=constraints)
            
            self.sql_generator_module = SQLGenerator()
            self.sql_generator_module.load(compiled_sql_path)
            print("Loaded compiled SQL Generator.")
        else:
            self.sql_generator_module = dspy.ChainOfThought(GenerateSQL)
            
        self.synthesizer_module = dspy.ChainOfThought(SynthesizeAnswer)
        
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("router", self.router_node)
        workflow.add_node("retriever", self.retriever_node)
        workflow.add_node("planner", self.planner_node)
        workflow.add_node("sql_generator", self.sql_generator_node)
        workflow.add_node("executor", self.executor_node)
        workflow.add_node("synthesizer", self.synthesizer_node)
        workflow.add_node("repair", self.repair_node)
        
        workflow.set_entry_point("router")
        
        workflow.add_conditional_edges(
            "router",
            lambda state: state["classification"],
            {
                "rag": "retriever",
                "sql": "sql_generator",
                "hybrid": "retriever"
            }
        )
        
        workflow.add_edge("retriever", "planner")
        
        workflow.add_conditional_edges(
            "planner",
            lambda state: state["classification"],
            {
                "rag": "synthesizer",
                "hybrid": "sql_generator"
            }
        )
        
        workflow.add_edge("sql_generator", "executor")
        
        workflow.add_conditional_edges(
            "executor",
            lambda state: "repair" if state.get("error") else "synthesizer"
        )
        
        workflow.add_conditional_edges(
            "repair",
            lambda state: "sql_generator" if state["repair_count"] < 2 else "synthesizer"
        )
        
        workflow.add_edge("synthesizer", END)
        
        return workflow.compile()

    def router_node(self, state: AgentState):
        pred = self.router_module(question=state["question"])
        return {"classification": pred.classification.lower()}

    def retriever_node(self, state: AgentState):
        docs = self.retriever.retrieve(state["question"])
        return {"retrieved_docs": docs}

    def planner_node(self, state: AgentState):
        context = "\n\n".join([d['content'] for d in state.get("retrieved_docs", [])])
        pred = self.planner_module(question=state["question"], context=context)
        return {"constraints": pred.constraints}

    def sql_generator_node(self, state: AgentState):
        # Include previous error in prompt if repairing
        question = state["question"]
        if state.get("error"):
            question += f"\n\nPrevious Error: {state['error']}. Please fix the query."
            
        pred = self.sql_generator_module(
            question=question,
            db_schema=str(self.schema),
            constraints=state.get("constraints", "")
        )
        # Extract SQL from code block if present
        sql = pred.sql_query
        if "```sql" in sql:
            sql = sql.split("```sql")[1].split("```")[0].strip()
        elif "```" in sql:
            sql = sql.split("```")[1].split("```")[0].strip()
            
        return {"sql_query": sql}

    def executor_node(self, state: AgentState):
        result = self.sqlite_tool.execute_query(state["sql_query"])
        if result["error"]:
            return {"error": result["error"], "sql_result": {}}
        return {"sql_result": result, "error": None}

    def repair_node(self, state: AgentState):
        return {"repair_count": state.get("repair_count", 0) + 1}

    def synthesizer_node(self, state: AgentState):
        # Prepare citations
        docs = state.get("retrieved_docs", [])
        doc_ids = [d['id'] for d in docs]
        
        # Simple heuristic for table citations based on SQL
        sql = state.get("sql_query", "").lower()
        tables = ["orders", "order_items", "products", "customers"]
        table_citations = [t for t in tables if t in sql]
        
        # We let the model decide final citations but pass these as context if needed
        # Actually the signature asks for citations as output, so we rely on the model
        
        pred = self.synthesizer_module(
            question=state["question"],
            sql_result=str(state.get("sql_result", {})),
            retrieved_docs=str(docs),
            format_hint=state["format_hint"]
        )
        
        # Parse citations from string if needed, or trust DSPy to return list
        # DSPy OutputField might return string representation of list
        citations = pred.citations
        if isinstance(citations, str):
            # Attempt to parse
            try:
                import ast
                citations = ast.literal_eval(citations)
            except:
                citations = [citations]
                
        # Ensure citations include doc ids and tables
        # This is a bit loose, but we'll trust the model for now or refine later
        
        return {
            "final_answer": pred.final_answer,
            "explanation": pred.explanation,
            "citations": citations
        }
