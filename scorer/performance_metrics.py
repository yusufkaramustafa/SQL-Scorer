from sqlalchemy import create_engine, text, Column, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, UTC
import numpy as np
from scorer.query_matcher import get_query_group, QuerySimilarity

# Database setup
DB_URL = "sqlite:///test.db"
engine = create_engine(DB_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class QueryPerformance(Base):
    __tablename__ = 'query_performance'
    
    id = Column(String, primary_key=True)
    execution_time = Column(Float)
    cpu_usage = Column(Float)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))
    query_hash = Column(String)  # Hash of the query for grouping similar queries
    query_text = Column(String)  # Store the original query text

# Create tables
Base.metadata.create_all(engine)

def store_performance_metrics(execution_time, cpu_usage, query):
    """Store performance metrics for a query"""
    session = Session()
    try:
        query_group = get_query_group(query)
        performance = QueryPerformance(
            id=f"{query_group}_{datetime.now(UTC).timestamp()}",
            execution_time=execution_time,
            cpu_usage=cpu_usage,
            query_hash=query_group,
            query_text=query
        )
        session.add(performance)
        session.commit()
    finally:
        session.close()

def find_similar_queries(query, session, threshold=0.8):
    """Find similar queries in the database"""
    query_group = get_query_group(query)
    recent_queries = session.query(QueryPerformance).order_by(
        QueryPerformance.timestamp.desc()
    ).limit(100).all()
    
    similar_queries = []
    for q in recent_queries:
        similarity = QuerySimilarity.calculate_similarity(query, q.query_text)
        if similarity >= threshold:
            similar_queries.append(q)
    
    return similar_queries

def calculate_dynamic_thresholds(query=None, window_size=100):
    """
    Calculate dynamic thresholds based on historical data
    If query is provided, thresholds are calculated for similar queries
    """
    session = Session()
    try:
        if query:
            # Find similar queries
            similar_queries = find_similar_queries(query, session)
            if not similar_queries:
                return 1.0, 100.0
            
            # Use similar queries for threshold calculation
            exec_times = [q.execution_time for q in similar_queries]
            cpu_usages = [q.cpu_usage for q in similar_queries]
        else:
            # Get recent performance data
            recent_data = session.query(QueryPerformance).order_by(
                QueryPerformance.timestamp.desc()
            ).limit(window_size).all()
            
            if not recent_data:
                return 1.0, 100.0
            
            exec_times = [p.execution_time for p in recent_data]
            cpu_usages = [p.cpu_usage for p in recent_data]
        
        # Calculate 95th percentile for thresholds
        exec_threshold = np.percentile(exec_times, 95)
        cpu_threshold = np.percentile(cpu_usages, 95)
        
        return float(exec_threshold), float(cpu_threshold)
    finally:
        session.close()

def calculate_performance_score(execution_time, cpu_usage, query=None):
    """
    Calculate performance score using dynamic thresholds
    Returns a score between 0 and 50
    """
    exec_threshold, cpu_threshold = calculate_dynamic_thresholds(query)
    
    exec_score = max(0, 25 * (1 - (execution_time / exec_threshold)))
    cpu_score = max(0, 25 * (1 - (cpu_usage / cpu_threshold)))
    
    return exec_score + cpu_score 