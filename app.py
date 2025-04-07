import streamlit as st
from scorer.scorer import score_query
import sqlfluff

def get_optimized_query(query: str) -> str:
    """Get the optimized version of a query using sqlfluff"""
    try:
        return sqlfluff.fix(query, dialect="postgres") or query
    except Exception as e:
        st.error(f"Error optimizing query: {e}")
        return query

def main():
    st.title("SQL Query Scorer")
    st.write("Compare and optimize your SQL queries")

    # Create two columns for query input
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Query 1")
        query1 = st.text_area("Enter first SQL query", height=200)

    with col2:
        st.subheader("Query 2")
        query2 = st.text_area("Enter second SQL query", height=200)

    if st.button("Compare Queries"):
        if not query1 or not query2:
            st.warning("Please enter both queries")
            return

        # Score both queries
        score1 = score_query(query1)
        score2 = score_query(query2)

        # Display results
        st.header("Results")
        
        # Create columns for results
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            st.subheader("Query 1 Results")
            st.metric("Score", f"{score1['score']:.2f}")
            st.write("Performance:", score1["score_breakdown"]["performance"])
            st.write("Optimization:", score1["score_breakdown"]["optimization"])
            st.write("Readability:", score1["score_breakdown"]["readability"])
            
        with res_col2:
            st.subheader("Query 2 Results")
            st.metric("Score", f"{score2['score']:.2f}")
            st.write("Performance:", score2["score_breakdown"]["performance"])
            st.write("Optimization:", score2["score_breakdown"]["optimization"])
            st.write("Readability:", score2["score_breakdown"]["readability"])

        # Show winner
        st.header("Winner")
        if score1["score"] > score2["score"]:
            st.success("Query 1 performed better!")
            better_query = query1
        else:
            st.success("Query 2 performed better!")
            better_query = query2

        # Show optimized version
        st.subheader("Optimized Version")
        optimized = get_optimized_query(better_query)
        st.code(optimized, language="sql")

if __name__ == "__main__":
    main()
