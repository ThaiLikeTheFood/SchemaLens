"""
 Author: Thai Tran
 Specialized purpose file to quantify tokanage and optimizations for time / savings.
 Not relevant to main structure's performance, purely for reference
"""

import time
import tiktoken
from pydantic import BaseModel
from app.governance import sanitize_and_limit_sql, SecurityViolation

class BenchmarkResponse(BaseModel):
    naive_context_tokens: int
    schemalens_tokens: int
    token_reduction_pct: str
    safety_rejections_tested: bool
    gateway_overhead_ms: float

# Simulate the massive DDL dump an agent usually receives in an unoptimized system
NAIVE_FULL_DDL = """
CREATE TABLE claimants (id INT PRIMARY KEY, ssn_hash VARCHAR UNIQUE, full_name VARCHAR, claim_status VARCHAR);
CREATE TABLE disbursements (id INT PRIMARY KEY, claimant_id INT, amount FLOAT, issue_date DATE);
CREATE TABLE appeals (id INT PRIMARY KEY, claimant_id INT, reason VARCHAR, status VARCHAR);
-- Imagine 50 more tables here for a real enterprise database...
""" * 20  # Multiplied to simulate a real-world enterprise schema weight

# Simulate the compressed JSON response from our /mcp/discover route
OPTIMIZED_DISCOVERY = """
{"claimants": {"columns": ["id (INT, PK)", "ssn_hash (VARCHAR, UNIQUE)", "full_name (VARCHAR)", "claim_status (VARCHAR)"], "relations": ["disbursements.claimant_id", "appeals.claimant_id"]}}
"""

def count_tokens(text: str) -> int:
    """Counts tokens using the cl100k_base encoding (used by GPT-4 and modern frontier models)."""
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

def run_performance_benchmark() -> BenchmarkResponse:
    """
    Executes a live benchmark comparing token usage and measuring AST parsing overhead.
    """
    # 1. Token Metrics
    naive_tokens = count_tokens(NAIVE_FULL_DDL)
    optimized_tokens = count_tokens(OPTIMIZED_DISCOVERY)
    reduction = ((naive_tokens - optimized_tokens) / naive_tokens) * 100

    # 2. Security & Overhead Metrics
    start_time = time.perf_counter()
    safety_passed = False
    
    try:
        # We intentionally throw a malicious query at our governance engine
        sanitize_and_limit_sql("SELECT * FROM claimants; DROP TABLE disbursements;")
    except SecurityViolation:
        # The AST parser successfully caught the DROP TABLE command
        safety_passed = True
        
    overhead_ms = round((time.perf_counter() - start_time) * 1000, 3)

    return BenchmarkResponse(
        naive_context_tokens=naive_tokens,
        schemalens_tokens=optimized_tokens,
        token_reduction_pct=f"{reduction:.2f}%",
        safety_rejections_tested=safety_passed,
        gateway_overhead_ms=overhead_ms
    )