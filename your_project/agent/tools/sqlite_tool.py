import sqlite3
import pandas as pd

class SQLiteTool:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_schema(self):
        """Get the schema of the database (tables and columns)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get list of tables/views
        cursor.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view');")
        tables = [row[0] for row in cursor.fetchall()]
        
        schema_info = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info('{table}');")
            columns = cursor.fetchall()
            # Format: (cid, name, type, notnull, dflt_value, pk)
            schema_info[table] = [f"{col[1]} ({col[2]})" for col in columns]
            
        conn.close()
        return schema_info

    def execute_query(self, query):
        """Execute a read-only SQL query and return results."""
        # Basic safety check
        if not query.strip().lower().startswith("select"):
            return {"error": "Only SELECT queries are allowed."}
            
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(query, conn)
            conn.close()
            return {"columns": list(df.columns), "rows": df.to_dict(orient='records'), "error": None}
        except Exception as e:
            return {"columns": [], "rows": [], "error": str(e)}
