import time
import psutil
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from db.config import DB_URL

# Connect to SQLite
engine = create_engine(DB_URL)

def execute_sql(query):
    """Executes a SQL query and measures performance"""
    try:
        with engine.connect() as conn:
            start_time = time.time()
            process = psutil.Process()
            cpu_before = process.cpu_percent()

            result = conn.execute(text(query))
            conn.commit()

            cpu_after = process.cpu_percent()
            execution_time = time.time() - start_time
            return execution_time, cpu_after - cpu_before, result.rowcount
    except SQLAlchemyError as e:
        print(f"SQL execution error {e}")
        return None, None, None
    
def run_explain(query):
    """Runs EXPLAIN QUERY PLAN and returns insights"""
    try:
        with engine.connect() as conn:
            explain_result = conn.execute(text(f"EXPLAIN QUERY PLAN {query}"))
            rows = explain_result.fetchall()
            return rows
    except Exception as e:
        print(f"Failed to run EXPLAIN: {e}")
        return []