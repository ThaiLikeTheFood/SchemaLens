import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import text

# Import separated concerns
from app.config import settings
from app.schemas import DiscoverRequest, DiscoverResponse, ExecuteRequest, ExecuteResponse
from app.catalog import SCHEMA_CATALOG
from app.database import AsyncSessionLocal
from app.governance import sanitize_and_limit_sql, SecurityViolation
from app.telemetry import run_performance_benchmark, BenchmarkResponse


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise Schema Discovery & Governance Middleware for AI Agents.",
    version=settings.APP_VERSION
)

@app.get("/", include_in_schema=False)
async def root():
    """Redirects the homepage directly to the Swagger interactive documentation."""
    return RedirectResponse(url="/docs")

@app.post("/mcp/discover", response_model=DiscoverResponse, tags=["Discovery"])
async def discover_schema(request: DiscoverRequest):
    """
    Selective Schema Discovery: Returns only the requested table definitions 
    to prevent LLM context window satiation.
    """
    discovered = {}
    for entity in request.entities:
        entity_lower = entity.lower()
        if entity_lower in SCHEMA_CATALOG:
            discovered[entity_lower] = SCHEMA_CATALOG[entity_lower]
            
    if not discovered:
        raise HTTPException(status_code=404, detail="No matching entities found in the enterprise catalog.")
        
    return DiscoverResponse(
        schemas=discovered,
        message=f"Successfully discovered {len(discovered)} entities."
    )

@app.post("/mcp/execute", response_model=ExecuteResponse, tags=["Execution"])
async def execute_query(request: ExecuteRequest):
    """
    Deterministic Governance: Parses, validates, and executes the agent's SQL safely.
    """
    start_time = time.perf_counter()
    warnings = []

    try:
        # Use our centralized setting for the maximum row limit
        safe_sql = sanitize_and_limit_sql(request.sql_query, max_limit=settings.MAX_QUERY_LIMIT)
        if safe_sql != request.sql_query:
            warnings.append(f"Query rewritten: Deterministic LIMIT {settings.MAX_QUERY_LIMIT} automatically applied.")
    except SecurityViolation as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text(safe_sql))
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database execution error: {str(e)}")

    execution_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return ExecuteResponse(
        status="success",
        rows=rows,
        row_count=len(rows),
        execution_time_ms=execution_ms,
        warnings=warnings
    )

@app.get("/mcp/benchmark", response_model=BenchmarkResponse, tags=["Telemetry"])
async def execute_benchmark():
    """
    Executes a live side-by-side benchmark comparing an unoptimized full-schema dump 
    against SchemaLens targeted discovery, outputting live token savings and security metrics.
    """
    return run_performance_benchmark()