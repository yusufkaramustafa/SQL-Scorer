import sqlfluff
import sqlparse
from collections import defaultdict
from database import execute_sql, run_explain
from performance_metrics import store_performance_metrics, calculate_performance_score
import math

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

def calculate_normalized_score(base_score: float, penalties: float, max_penalties: float) -> float:
    """
    Calculate a normalized score using exponential decay for penalties
    base_score: Maximum possible score
    penalties: Current penalties
    max_penalties: Maximum possible penalties
    """
    if max_penalties == 0:
        return base_score
    
    # Normalize penalties to a value between 0 and 1
    normalized_penalties = min(penalties / max_penalties, 1.0)
    
    # Use exponential decay: score = base_score * e^(-k * normalized_penalties)
    # where k controls how quickly the score decays
    k = 2.0  # Adjust this value to control decay rate
    return base_score * math.exp(-k * normalized_penalties)

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

    # Store performance metrics for future threshold calculations
    store_performance_metrics(exec_time, cpu_usage, query)

    analysis = analyze_sql(query)
    violations = analysis["violation_summary"]

    # ---------- 1. Computational Performance (50 pts) ----------
    # Use dynamic thresholds for performance scoring
    perf_score = calculate_performance_score(exec_time, cpu_usage, query)

    # ---------- 2. Best Practices / Optimization (30 pts) ----------
    optimization_categories = [
        "aliasing.table", "ambiguous.join", "unnecessary.subquery"
    ]
    # Calculate penalties and maximum possible penalties
    opt_penalties = sum(violations.get(cat, 0) for cat in optimization_categories) * 5
    max_opt_penalties = len(optimization_categories) * 5  # Maximum possible penalties
    
    # Calculate normalized optimization score
    opt_score = calculate_normalized_score(30, opt_penalties, max_opt_penalties)
    # Add explain score (up to 10 points) proportionally
    opt_score = min(30, opt_score + explain_score)

    # ---------- 3. Readability / Layout (20 pts) ----------
    readability_categories = [k for k in violations if k.startswith("layout.") or k.startswith("indent.")]
    # Calculate penalties and maximum possible penalties
    read_penalties = sum(violations[k] for k in readability_categories) * 2
    max_read_penalties = len(readability_categories) * 2  # Maximum possible penalties
    
    # Calculate normalized readability score
    read_score = calculate_normalized_score(20, read_penalties, max_read_penalties)

    # ---------- Total Score ----------
    total_score = round(perf_score + opt_score + read_score, 2)

    return {
        "execution_time": exec_time,
        "cpu_usage": cpu_usage,
        "rows_affected": row_count,
        "formatted_query": analysis["formatted_query"],
        "violation_summary": violations,
        "explain_plan": [row[3] for row in plan_rows],
        "explain_notes": explain_notes,
        "score_breakdown": {
            "performance": perf_score,
            "optimization": opt_score,
            "readability": read_score
        },
        "score": total_score
    }