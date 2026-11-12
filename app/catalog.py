"""
Author: Thai Tran

 In a production environment, this would dynamically introspect the database.
 For our middleware demonstration, we use a static in-memory catalog graph.
"""
SCHEMA_CATALOG = {
    "claimants": {
        "columns": ["id (INT, PK)", "ssn_hash (VARCHAR, UNIQUE)", "full_name (VARCHAR)", "claim_status (VARCHAR)"],
        "relations": ["disbursements.claimant_id", "appeals.claimant_id"]
    },
    "disbursements": {
        "columns": ["id (INT, PK)", "claimant_id (INT, FK)", "amount (FLOAT)", "issue_date (DATE)"]
    },
    "appeals": {
        "columns": ["id (INT, PK)", "claimant_id (INT, FK)", "reason (VARCHAR)", "status (VARCHAR)"]
    }
}