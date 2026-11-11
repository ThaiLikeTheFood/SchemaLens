from pathlib import Path

class Settings:
    # Application Metadata
    APP_NAME: str = "SchemaLens Gateway (GovMCP)"
    APP_VERSION: str = "1.0.0"
    
    # Path Resolution
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    DB_PATH: Path = DATA_DIR / "gps_records.db"
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DB_PATH}"

    # Governance Guardrails
    MAX_QUERY_LIMIT: int = 100
    DB_POOL_SIZE: int = 5
    DB_POOL_TIMEOUT: float = 3.0

settings = Settings()