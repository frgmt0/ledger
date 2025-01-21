"""
Database storage operations for the ledger application.
"""
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from typing import Generator, List, Optional

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from .config import DATABASE_URL
from .models import Base, Transaction

engine = create_engine(DATABASE_URL)

# Create all tables
Base.metadata.create_all(engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get a database session."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_transaction(
    date: datetime,
    description: str,
    amount: Decimal,
    category: Optional[str] = None,
    notes: Optional[str] = None,
) -> Transaction:
    """Create a new transaction."""
    transaction = Transaction(
        date=date,
        description=description,
        amount=amount,
        category=category,
        notes=notes,
    )
    
    with get_db() as db:
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
    
    return transaction


def get_transactions(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[str] = None,
) -> List[Transaction]:
    """Get transactions with optional filtering."""
    query = select(Transaction)
    
    if start_date:
        query = query.where(Transaction.date >= start_date)
    if end_date:
        query = query.where(Transaction.date <= end_date)
    if category:
        query = query.where(Transaction.category == category)
    
    return list(db.scalars(query))
