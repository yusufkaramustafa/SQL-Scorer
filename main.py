from scorer.scorer import score_query
import sqlfluff
import argparse

def get_optimized_query(query):
    """Get the optimized version of a query using sqlfluff"""
    try:
        return sqlfluff.fix(query, dialect="postgres") or query
    except Exception as e:
        print(f"Error optimizing query: {e}")
        return query

def main():
    parser = argparse.ArgumentParser(description="SQL Query Scorer and Optimizer")
    parser.add_argument("query1", help="First SQL query file")
    parser.add_argument("query2", help="Second SQL query file")
    args = parser.parse_args()


    try:
        with open(args.query1, "r") as f1, open(args.query2, "r") as f2:
            query1, query2 = f1.read().strip(), f2.read().strip()
    except Exception as e:
        print(f"Error reading files: {e}")
        return

    
    score1 = score_query(query1)
    score2 = score_query(query2)

    
    if score1["score"] > score2["score"]:
        better_query = query1
        better_score = score1["score"]
        print(f"\nQuery 1 performed better with score: {better_score}")
    else:
        better_query = query2
        better_score = score2["score"]
        print(f"\nQuery 2 performed better with score: {better_score}")

    
    print("\nOptimized version of the better query:")
    print(get_optimized_query(better_query))

if __name__ == "__main__":
    main()