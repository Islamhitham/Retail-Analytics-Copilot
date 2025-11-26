import dspy

class Router(dspy.Signature):
    """Classify the user question into one of the following categories: 'rag', 'sql', or 'hybrid'.
    
    - 'rag': Questions about policies, marketing calendar, or definitions found in text documents.
    - 'sql': Questions requiring data aggregation or retrieval from the database (e.g., revenue, top products).
    - 'hybrid': Questions that need both document context (e.g., specific date ranges from calendar, KPI definitions) and database data.
    """
    question = dspy.InputField(desc="The user's question about retail analytics.")
    classification = dspy.OutputField(desc="The classification: 'rag', 'sql', or 'hybrid'.")

class Planner(dspy.Signature):
    """Extract constraints and entities from the question to guide the answer generation.
    
    Identify date ranges, specific product categories, KPI definitions to use, and any other constraints.
    """
    question = dspy.InputField(desc="The user's question.")
    context = dspy.InputField(desc="Retrieved document chunks relevant to the question.")
    constraints = dspy.OutputField(desc="Extracted constraints (e.g., date ranges, categories, formulas).")

class GenerateSQL(dspy.Signature):
    """Generate a valid SQLite query to answer the question based on the schema and constraints.
    
    Use the provided schema and constraints. 
    - Use 'orders', 'order_items', 'products', 'customers' views/tables.
    - Revenue = SUM(UnitPrice * Quantity * (1 - Discount)).
    - AOV = SUM(Revenue) / COUNT(DISTINCT OrderID).
    - Gross Margin = SUM((UnitPrice - CostOfGoods) * Quantity * (1 - Discount)).
    - If CostOfGoods is missing, assume 0.7 * UnitPrice.
    """
    question = dspy.InputField(desc="The user's question.")
    db_schema = dspy.InputField(desc="Schema of the available tables/views.")
    constraints = dspy.InputField(desc="Constraints and definitions extracted from documents.")
    sql_query = dspy.OutputField(desc="The SQLite query to execute.")

class SynthesizeAnswer(dspy.Signature):
    """Synthesize the final answer based on the question, SQL results, and retrieved documents.
    
    Ensure the answer matches the requested format exactly.
    Include citations for all used database tables and document chunks.
    """
    question = dspy.InputField(desc="The user's question.")
    sql_result = dspy.InputField(desc="Result of the executed SQL query (if any).")
    retrieved_docs = dspy.InputField(desc="Relevant document chunks with IDs.")
    format_hint = dspy.InputField(desc="The required format for the final answer.")
    
    final_answer = dspy.OutputField(desc="The answer matching the format_hint.")
    explanation = dspy.OutputField(desc="Brief explanation (<= 2 sentences).")
    citations = dspy.OutputField(desc="List of citations (tables and doc chunk IDs).")
