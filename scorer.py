import sqlfluff
import sqlparse
from collections import defaultdict
from database import execute_sql

def analyze_sql(query):
    """Analyzes SQL Query Readability & Best Practices"""
    parsed = sqlparse.format(query, reindent=True)
    lint_result = sqlfluff.lint(parsed, dialect="postgres")

    categorized = defaultdict(int)

    for v in lint_result:
        category = v.get("name", "unknown")
        categorized[category] += 1

    return {
        "violation_summary": dict(categorized),
        "formatted_query": parsed,
    }

def score_query(query):
    """Executes and scores a query"""
    exec_time, cpu_usage, row_count = execute_sql(query)
    if exec_time is None:
        return {
            "error": "Query execution failed.",
            "execution_time": None,
            "cpu_usage": None,
            "rows_affected": None,
            "violations": [],
            "violation_summary": {}
        }
    
    analysis = analyze_sql(query)

    return {
        "execution_time": exec_time,
        "cpu_usage": cpu_usage,
        "rows_affected": row_count,
        "formatted_query": analysis["formatted_query"],
        "violation_summary": analysis["violation_summary"]
    }