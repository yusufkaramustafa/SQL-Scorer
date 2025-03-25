import sqlfluff
import sqlparse
from collections import defaultdict
from database import execute_sql, run_explain

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

def analyze_explain_plan(plan_rows):
    """Analyzes EXPLAIN QUERY PLAN output and returns score and notes"""
    penalties = 0
    notes = []

    for row in plan_rows:
        detail = row[3].upper() 
        if "SCAN" in detail and "USING INDEX" not in detail:
            penalties += 5
            notes.append(f"Full table scan: '{detail}'")
        if "SUBQUERY" in detail:
            penalties += 3
            notes.append(f"Subquery usage: '{detail}'")
        if "USING INDEX" in detail:
            notes.append(f"Index usage: '{detail}'")

    explain_score = max(0, 10 - penalties)  
    return explain_score, notes

def score_query(query):
    exec_time, cpu_usage, row_count = execute_sql(query)
    plan_rows = run_explain(query)
    explain_score, explain_notes = analyze_explain_plan(plan_rows)

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
    opt_score = max(0, 30 - opt_penalty + explain_score)  

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
        "explain_plan": [row[3] for row in plan_rows],  #
        "explain_notes": explain_notes,
        "score_breakdown": {
            "performance": perf_score,
            "optimization": opt_score,
            "readability": read_score
        },
        "score": total_score
    }