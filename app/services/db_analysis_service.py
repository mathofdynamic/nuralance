# app/services/db_analysis_service.py
import sqlite3
import csv
from openai import OpenAI
import os
import re
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the model name as a constant for easy updates
ANALYZER_MODEL = "gpt-4.1-nano-2025-04-14"

def sanitize_name(name: str) -> str:
    """Sanitizes a string to be a valid SQL table/column name."""
    name = re.sub(r'[^a-zA-Z0-9_]', '', name)
    name = name.replace(' ', '_')
    if not name:
        name = "unnamed_column"
    return name

def load_csv_to_sqlite(csv_path: str, db_path: str):
    """
    Loads data from a CSV file into a new SQLite database.
    The table name is derived from the CSV filename.
    """
    try:
        table_name = sanitize_name(os.path.basename(csv_path).split('.')[0])
        if not table_name:
            table_name = "financial_data"

        with open(csv_path, 'r', encoding='utf-8-sig') as csv_file:
            reader = csv.reader(csv_file)
            header = [sanitize_name(col) for col in next(reader)]
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
            columns_with_types = ', '.join([f'"{col}" TEXT' for col in header])
            create_table_sql = f"CREATE TABLE `{table_name}` ({columns_with_types});"
            cursor.execute(create_table_sql)
            
            placeholders = ', '.join(['?'] * len(header))
            insert_sql = f"INSERT INTO `{table_name}` VALUES ({placeholders})"
            
            for row in reader:
                cursor.execute(insert_sql, row)
            
            conn.commit()
            conn.close()

    except Exception as e:
        print(f"Error loading CSV to SQLite: {e}")
        raise

def get_db_schema(db_path: str) -> str:
    """Connects to a SQLite DB and extracts its schema in a formatted string."""
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        schema_info = "The user has provided a database with the following schema:\n"
        for table_name_tuple in tables:
            table_name = table_name_tuple[0]
            if table_name.startswith('sqlite_'): continue
            
            schema_info += f"\nCREATE TABLE `{table_name}` (\n"
            cursor.execute(f"PRAGMA table_info(`{table_name}`);")
            columns = cursor.fetchall()
            for col in columns:
                schema_info += f"  `{col[1]}` {col[2]},\n"
            schema_info = schema_info.rstrip(',\n') + "\n);\n"
        
        conn.close()
        return schema_info
    except Exception as e:
        raise ValueError(f"Could not analyze the database schema. Error: {e}")

def generate_system_prompt(db_path: str) -> str:
    """
    Analyzes the database schema and uses an LLM to generate a dynamic system prompt.
    """
    schema_details = get_db_schema(db_path)
    
    table_name = "financial_data" # Default name
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        first_table = cursor.fetchone()
        if first_table:
            table_name = first_table[0]
        conn.close()
    except Exception as e:
        print(f"Could not dynamically get table name, using default. Error: {e}")

    try:
        response = client.chat.completions.create(
            model=ANALYZER_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert SQL data analyst. Your task is to create a concise and "
                        "effective system prompt for another AI assistant based on the provided SQLite database schema. "
                        "This prompt will guide the assistant to answer questions about a user's financial data."
                    )
                },
                {
                    "role": "user",
                    "content": f"""
                    Here is the schema from a user's database, which was loaded from a CSV file:
                    ---
                    {schema_details}
                    ---
                    Based on this schema, generate a system prompt for a financial AI assistant named Nuralance. The prompt MUST:
                    1.  Start with its identity: "You are Nuralance, an expert financial AI assistant."
                    2.  Briefly interpret the purpose of the main table based on its columns (e.g., 'The `{table_name}` table appears to track sales records...').
                    3.  Instruct the assistant that it MUST answer user questions by generating **read-only SQLite queries** and calling the `run_sql_query` function.
                    4.  Emphasize that it should ONLY use the table and column names explicitly provided in the schema, using backticks for identifiers (e.g., `product_name`).
                    5.  Instruct it to perform calculations (SUM, AVG, COUNT), and sorting directly within the SQL query for efficiency.
                    6.  Provide a clear, complex example query relevant to the schema, such as finding top-selling products.
                    7.  End with a friendly closing.

                    Return ONLY the generated system prompt, without any extra text or explanations.
                    """
                }
            ],
            temperature=0.2,
        )
        system_prompt = response.choices[0].message.content.strip()
        print(f"INFO: System Prompt generated successfully using {ANALYZER_MODEL}.")
        return system_prompt
    except Exception as e:
        print(f"ERROR: Failed to generate system prompt with OpenAI: {e}")
        return f"You are Nuralance, an expert financial AI assistant. The user's database schema is:\n{schema_details}\nAnswer questions by generating read-only SQLite queries for the `run_sql_query` function."