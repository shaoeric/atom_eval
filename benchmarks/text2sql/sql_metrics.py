import re
from typing import List, Dict, Any, Optional
from evalscope.api.metric import Metric
from evalscope.api.registry import register_metric

def sql_tokenize(sql: str) -> List[str]:
    """Simple tokenizer for SQL."""
    # 1. Lowercase
    sql = sql.lower()
    # 2. Extract strings, numbers, operators, and words
    # This regex handles single quotes, double quotes, numbers, words, and common operators
    tokens = re.findall(r"'(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|\d+\.?\d*|\w+|[<>=!]+|[(),;.*]", sql)
    return tokens

def normalize_sql_tokens(tokens: List[str]) -> List[str]:
    """Normalize tokens by replacing literals with placeholders."""
    normalized = []
    for token in tokens:
        if token.startswith("'") or token.startswith('"'):
            normalized.append("<STR>")
        elif re.match(r"^\d+\.?\d*$", token):
            normalized.append("<NUM>")
        else:
            normalized.append(token)
    return normalized

def build_simple_ast(tokens: List[str]) -> Dict[str, Any]:
    """A very simple 'AST' builder that groups tokens by main SQL clauses."""
    ast = {}
    current_clause = None
    # Common SQL clauses to group by
    clauses = ['select', 'from', 'where', 'group by', 'order by', 'limit', 'having', 'join', 'left join', 'right join', 'on']
    
    i = 0
    while i < len(tokens):
        # Check for multi-word clauses first (e.g., 'group by')
        found_clause = None
        for clause in clauses:
            clause_tokens = clause.split()
            if tokens[i:i+len(clause_tokens)] == clause_tokens:
                found_clause = clause
                i += len(clause_tokens) - 1
                break
        
        if found_clause:
            current_clause = found_clause
            if current_clause not in ast:
                ast[current_clause] = []
        elif current_clause:
            ast[current_clause].append(tokens[i])
        else:
            # Tokens before any major clause
            if 'other' not in ast:
                ast['other'] = []
            ast['other'].append(tokens[i])
        i += 1
    return ast

def ast_similarity(ast1: Dict[str, Any], ast2: Dict[str, Any]) -> float:
    """Compare two simple ASTs using clause-level similarity."""
    all_clauses = set(ast1.keys()) | set(ast2.keys())
    if not all_clauses:
        return 1.0
    
    clause_scores = []
    for clause in all_clauses:
        tokens1 = ast1.get(clause, [])
        tokens2 = ast2.get(clause, [])
        
        if not tokens1 and not tokens2:
            clause_scores.append(1.0)
        elif not tokens1 or not tokens2:
            clause_scores.append(0.0)
        else:
            # Jaccard similarity for the tokens in the clause
            set1 = set(tokens1)
            set2 = set(tokens2)
            intersection = set1 & set2
            union = set1 | set2
            clause_scores.append(len(intersection) / len(union) if union else 1.0)
            
    return sum(clause_scores) / len(clause_scores) if clause_scores else 0.0

@register_metric(name='sql_ast_sim')
class SQLASTSimilarity(Metric):
    """Metric for calculating SQL AST similarity based on normalized tokens and clauses."""
    
    def apply(self, predictions: List[str], references: List[str]) -> List[float]:
        results = []
        for pred, ref in zip(predictions, references):
            if not pred or not isinstance(pred, str):
                results.append(0.0)
                continue
            if not ref or not isinstance(ref, str):
                results.append(0.0)
                continue
            
            pred = pred.replace('\n', ' ').strip(';')
            ref = ref.replace('\n', ' ').strip(';')

            # Tokenize and normalize
            pred_tokens = normalize_sql_tokens(sql_tokenize(pred))
            ref_tokens = normalize_sql_tokens(sql_tokenize(ref))
            
            # Build simple AST structure
            pred_ast = build_simple_ast(pred_tokens)
            ref_ast = build_simple_ast(ref_tokens)
            
            # Calculate similarity
            results.append(ast_similarity(pred_ast, ref_ast))
        return results
