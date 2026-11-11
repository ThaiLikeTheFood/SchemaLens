# Author: Thai Tran
# Dynamic database pulling from 'Settings'.
# Storage layer is strictly decoupled from configuration

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date

# Import our centralized settings
from app.config import settings

# 1. Connection Pool Safeguards configured via settings
engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=False,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=0,       
    pool_timeout=settings.DB_POOL_TIMEOUT
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

# 2. Public Sector Entity Definitions
class Claimant(Base):
    __tablename__ = "claimants"
    id = Column(Integer, primary_key=True, index=True)
    ssn_hash = Column(String, unique=True, index=True) 
    full_name = Column(String)
    claim_status = Column(String)

class Disbursement(Base):
    __tablename__ = "disbursements"
    id = Column(Integer, primary_key=True, index=True)
    claimant_id = Column(Integer, ForeignKey("claimants.id"))
    amount = Column(Float)
    issue_date = Column(Date)

class Appeal(Base):
    __tablename__ = "appeals"
    id = Column(Integer, primary_key=True, index=True)
    claimant_id = Column(Integer, ForeignKey("claimants.id"))
    reason = Column(String)
    status = Column(String)

# 3. Automatic Seeding for the Demo
async def init_db():
    from datetime import date
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        c1 = Claimant(ssn_hash="a1b2c3d4", full_name="Jane Doe", claim_status="ACTIVE")
        c2 = Claimant(ssn_hash="e5f6g7h8", full_name="John Smith", claim_status="SUSPENDED")
        
        session.add_all([c1, c2])
        await session.commit()

        d1 = Disbursement(claimant_id=c1.id, amount=450.00, issue_date=date(2023, 10, 1))
        d2 = Disbursement(claimant_id=c1.id, amount=450.00, issue_date=date(2023, 11, 1))
        a1 = Appeal(claimant_id=c2.id, reason="Missed recertification deadline", status="PENDING_REVIEW")
        
        session.add_all([d1, d2, a1])
        await session.commit()
        print(f"Database initialized and seeded successfully at: {settings.DB_PATH}")

if __name__ == "__main__":
    asyncio.run(init_db())