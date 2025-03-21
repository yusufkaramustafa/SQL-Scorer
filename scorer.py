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
    exec_time, cpu_usage, row_count = execute_sql(query)
    if exec_time is None:
        return {
            "error": "Query execution failed.",
            "execution_time": None,
            "cpu_usage": None,
            "rows_affected": None,
            "violations": [],
            "violation_summary": {},
            "score": 0
        }

    analysis = analyze_sql(query)
    violations = analysis["violation_summary"]

    # ---------- 1. Computational Performance (50 pts) ----------
    # Normalize execution time and CPU to a 0-50 score
    max_exec_time = 1.0 
    max_cpu = 100  

    perf_score = max(0, 50 - (exec_time / max_exec_time * 25 + cpu_usage / max_cpu * 25))

    # ---------- 2. Best Practices / Optimization (30 pts) ----------
    optimization_categories = [
        "aliasing.table", "ambiguous.join", "unnecessary.subquery"
    ]
    opt_penalty = sum(violations.get(cat, 0) for cat in optimization_categories) * 5
    opt_score = max(0, 30 - opt_penalty)

    # ---------- 3. Readability / Layout (20 pts) ----------
    readability_categories = [k for k in violations if k.startswith("layout.") or k.startswith("indent.")]
    read_penalty = sum(violations[k] for k in readability_categories) * 2
    read_score = max(0, 20 - read_penalty)

    # ---------- Total Score ----------
    total_score = round(perf_score + opt_score + read_score, 2)

    return {
        "execution_time": exec_time,
        "cpu_usage": cpu_usage,
        "rows_affected": row_count,
        "formatted_query": analysis["formatted_query"],
        "violation_summary": violations,
        "score_breakdown": {
            "performance": perf_score,
            "optimization": opt_score,
            "readability": read_score
        },
        "score": total_score
    }