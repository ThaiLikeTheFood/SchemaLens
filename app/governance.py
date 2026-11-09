# Author: Thai Tran
# SECURITY AND MIDDLEWARE LAYER
# THIS LAYER HANDLES EVERY SQL STRING THE AI AGENT RECEIVES.
# UTILIZE AST OVER REGEX TO PREVENT PROMPT ENGINEERING

import sqlglot
from sqlglot import exp

class SecurityViolation(Exception):
    """Custom exception raised when an agent attempts a forbidden database operation."""
    pass

def sanitize_and_limit_sql(raw_sql: str, max_limit: int = 100) -> str:
    """
    Parses, validates, and rewrites raw SQL from an AI agent.
    Enforces read-only SELECT operations and injects a hard limit.
    """
    try:
        parsed_statements = sqlglot.parse(raw_sql, read="sqlite")
    except sqlglot.errors.ParseError as exc:
        raise SecurityViolation(f"Agent generated invalid SQL syntax: {exc}")

    if not parsed_statements or len(parsed_statements) > 1:
        raise SecurityViolation("Multi-statement queries are strictly prohibited.")
    
    ast = parsed_statements[0]

    # Assert the root node is a SELECT statement
    if not isinstance(ast, exp.Select):
        raise SecurityViolation("Query must be an explicit SELECT statement. No DDL/DML allowed.")

    # Deep-walk AST to block any destructive nodes
    forbidden_nodes = (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Alter, exp.Command)
    for node in ast.walk():
        if isinstance(node, forbidden_nodes):
            raise SecurityViolation(f"Destructive operation detected and blocked: {node.key}")

    # 4. Deterministic LIMIT injection
    limit_node = ast.args.get("limit")
    if limit_node is None:
        # If no limit exists, inject our max_limit
        ast = ast.limit(max_limit)
    else:
        # If a limit exists, inspect its value and clamp it if it exceeds max_limit
        try:
            current_limit = int(limit_node.expression.this)
            if current_limit > max_limit:
                ast.args["limit"] = exp.Limit(this=exp.Literal.number(max_limit))
        except (ValueError, TypeError):
            # Fallback for dynamic/complex limits
            ast.args["limit"] = exp.Limit(this=exp.Literal.number(max_limit))

    return ast.sql(dialect="sqlite")

if __name__ == "__main__":
    test_queries = [
        ("SELECT full_name FROM claimants", "Valid basic select"),
        ("SELECT * FROM disbursements LIMIT 5000", "Select exceeding limit"),
        ("SELECT * FROM claimants; DROP TABLE appeals;", "Malicious multi-statement"),
        ("UPDATE claimants SET claim_status = 'ACTIVE'", "Malicious update")
    ]

    print("--- Running Governance Security Checks ---")
    for sql, description in test_queries:
        print(f"\nTesting [{description}]:\nInput: {sql}")
        try:
            safe_sql = sanitize_and_limit_sql(sql)
            print(f"Output: {safe_sql}")
        except SecurityViolation as e:
            print(f"BLOCKED: {e}")