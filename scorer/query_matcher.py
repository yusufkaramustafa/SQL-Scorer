import sqlparse
from sqlparse.sql import Token, Where, Comparison, Identifier, TokenList
from sqlparse.tokens import Keyword, DML, DDL, Punctuation, Number, String
import re
from difflib import SequenceMatcher
from typing import List, Tuple, Set

class QueryNormalizer:
    @staticmethod
    def normalize_parameters(query: str) -> str:
        """Replace parameter values with placeholders"""
        # Replace numbers
        query = re.sub(r'\b\d+\b', '?', query)
        # Replace string literals
        query = re.sub(r"'[^']*'", '?', query)
        return query

    @staticmethod
    def normalize_whitespace(query: str) -> str:
        """Normalize whitespace and case"""
        return ' '.join(query.lower().split())

    @staticmethod
    def extract_structure(parsed: sqlparse.sql.Statement) -> List[str]:
        """Extract query structure elements"""
        elements = []
        
        def process_token(token):
            if isinstance(token, Token):
                if token.ttype in (Keyword, DML, DDL):
                    elements.append(f"KEYWORD:{token.value.upper()}")
                elif token.ttype == Identifier:
                    elements.append(f"IDENTIFIER:{token.value.lower()}")
                elif token.ttype == Number:
                    elements.append("NUMBER")
                elif token.ttype == String:
                    elements.append("STRING")
                elif token.ttype == Punctuation:
                    elements.append(f"PUNCT:{token.value}")
            elif isinstance(token, Where):
                elements.append("WHERE")
                for item in token.tokens:
                    if isinstance(item, Comparison):
                        elements.append("COMPARISON")
                    else:
                        process_token(item)
            elif isinstance(token, TokenList):
                for item in token.tokens:
                    process_token(item)

        process_token(parsed)
        return elements

    @staticmethod
    def normalize_query(query: str) -> Tuple[str, List[str]]:
        """Normalize query and extract structure"""
        
        parsed = sqlparse.parse(query)[0]
        
        # Normalize parameters and whitespace
        normalized = QueryNormalizer.normalize_parameters(query)
        normalized = QueryNormalizer.normalize_whitespace(normalized)
        
        # Extract structure
        structure = QueryNormalizer.extract_structure(parsed)
        
        return normalized, structure

class QuerySimilarity:
    @staticmethod
    def string_similarity(s1: str, s2: str) -> float:
        """Calculate string similarity using SequenceMatcher"""
        return SequenceMatcher(None, s1, s2).ratio()

    @staticmethod
    def structure_similarity(s1: List[str], s2: List[str]) -> float:
        """Calculate structure similarity"""
        if not s1 or not s2:
            return 0.0
        
        # Convert to sets for comparison
        set1 = set(s1)
        set2 = set(s2)
        
        # Calculate Jaccard similarity
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0

    @staticmethod
    def calculate_similarity(query1: str, query2: str) -> float:
        """Calculate overall query similarity"""
        # Normalize both queries
        norm1, struct1 = QueryNormalizer.normalize_query(query1)
        norm2, struct2 = QueryNormalizer.normalize_query(query2)
        
        # Calculate string similarity
        string_sim = QuerySimilarity.string_similarity(norm1, norm2)
        
        # Calculate structure similarity
        struct_sim = QuerySimilarity.structure_similarity(struct1, struct2)
        
        # Weighted combination (60% string, 40% structure)
        return 0.6 * string_sim + 0.4 * struct_sim

def get_query_group(query: str, threshold: float = 0.8) -> str:
    """
    Generate a query group identifier based on similarity
    Returns a hash that represents similar queries
    """
    normalized, structure = QueryNormalizer.normalize_query(query)
    
    # Combine normalized query and structure for hashing
    combined = f"{normalized}|{'|'.join(structure)}"
    return combined 