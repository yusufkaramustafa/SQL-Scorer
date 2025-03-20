import sqlfluff
import sqlparse
from database import execute_sql

def analyze_sql(query):
    """Analyzes SQL Query Readability & Best Practices"""
    parsed = sqlparse.format(query, reindent=True)
    lint_result = sqlfluff.lint(parsed, dialect="postgres")

    return {
        "analysis": lint_result,  
        "formatted_query": parsed,
    }

def score_query(query):
    """Executes and scores a query"""
    exec_time, cpu_usage, row_count = execute_sql(query)
    analysis = analyze_sql(query)


    return {
        "execution_time": exec_time,
        "cpu_usage": cpu_usage,
        "rows_affected": row_count,
        "analysis": analysis
    }