import argparse
from scorer import score_query

def main():
    parser = argparse.ArgumentParser(description="SQL Scorer CLI")
    parser.add_argument("query1", type=str, help="Path to first SQL file")
    parser.add_argument("query2", type=str, help="Path to second SQL file")

    args = parser.parse_args()

    with open(args.query1, "r") as f1, open(args.query2, "r") as f2:
        sql1, sql2 = f1.read(), f2.read()

    result1 = score_query(sql1)
    result2 = score_query(sql2)
    print(result1['violation_summary'])
    print(result2['violation_summary'])

if __name__ == "__main__":
    main()