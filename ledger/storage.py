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

# Default categories to populate the database with
DEFAULT_CATEGORIES = [
    "Food", "Housing", "Transportation", "Utilities",
    "Healthcare", "Entertainment", "Shopping",
    "Education", "Income", "Other"
]


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


def get_or_create_category(db: Session, name: str) -> str:
    """Get existing category or create new one."""
    from .models import Category
    
    # Check if category exists
    category = db.query(Category).filter(Category.name == name).first()
    if not category:
        # Create new category
        category = Category(name=name)
        db.add(category)
        db.commit()
    
    return category.name

def delete_category(db: Session, name: str) -> bool:
    """Delete a category if it's not a default one.
    
    Returns:
        bool: True if category was deleted, False if it was a default category
    """
    from .models import Category
    
    if name in DEFAULT_CATEGORIES:
        return False
        
    category = db.query(Category).filter(Category.name == name).first()
    if category:
        db.delete(category)
        db.commit()
        return True
    return False

# Create all tables and initialize defaults
Base.metadata.create_all(engine)
with get_db() as db:
    initialize_default_categories(db)

def create_transaction(
    db: Session,
    date: datetime,
    description: str,
    amount: Decimal,
    category: Optional[str] = None,
) -> Transaction:
    """Create a new transaction."""
    # Create/get category if provided
    if category:
        category = get_or_create_category(db, category)
    
    # Create transaction
    transaction = Transaction(
        date=date,
        description=description,
        amount=amount,
        category=category,
    )
    
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
