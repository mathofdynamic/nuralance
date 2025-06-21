# app/services/query_execution_service.py

import sqlite3
import json

def run_sql_query(db_path: str, sql_query: str) -> str:
    """
    Executes a read-only SQL query on the specified SQLite database and returns the result as a JSON string.
    """
    # Security: Only allow SELECT statements to prevent data modification.
    if not sql_query.strip().upper().startswith("SELECT"):
        return json.dumps([{"error": "Invalid query. Only SELECT statements are permitted."}])

    try:
        # Connect in read-only mode for extra safety
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        
        cursor.execute(sql_query)
        
        column_names = [description[0] for description in cursor.description]
        results = [dict(zip(column_names, row)) for row in cursor.fetchall()]
        
        conn.close()
        
        if not results:
            return json.dumps([{"message": "Query executed successfully, but no results were found."}])

        # Return a clean JSON string representation of the results
        return json.dumps(results)

    except sqlite3.Error as e:
        return json.dumps([{"error": f"An SQL error occurred: {e}", "query_attempted": sql_query}])
    except Exception as e:
        return json.dumps([{"error": f"An unexpected error occurred: {e}"}])