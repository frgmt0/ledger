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
from .models import Base, Transaction, BankAccount

engine = create_engine(DATABASE_URL)

# Default categories to populate the database with
DEFAULT_CATEGORIES = [
    "Food", "Housing", "Transportation", "Utilities",
    "Healthcare", "Entertainment", "Shopping",
    "Education", "Income", "Other"
]


def initialize_default_categories(db: Session):
    """Initialize the database with default categories if empty."""
    from .models import Category
    
    existing_categories = db.query(Category).count()
    if existing_categories == 0:
        for category_name in DEFAULT_CATEGORIES:
            category = Category(name=category_name)
            db.add(category)
        db.commit()


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

def create_bank_account(
    db: Session,
    name: str,
    account_type: str,
    description: Optional[str] = None,
) -> BankAccount:
    """Create a new bank account."""
    account = BankAccount(
        name=name,
        account_type=account_type,
        description=description,
    )
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    return account

def get_bank_accounts(db: Session) -> List[BankAccount]:
    """Get all bank accounts."""
    return list(db.query(BankAccount).all())

def get_bank_account(db: Session, account_id: int) -> Optional[BankAccount]:
    """Get a specific bank account by ID."""
    return db.query(BankAccount).filter(BankAccount.id == account_id).first()

def create_transaction(
    db: Session,
    date: datetime,
    description: str,
    amount: Decimal,
    account_id: int,
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
        account_id=account_id,
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
    account_id: Optional[int] = None,
) -> List[Transaction]:
    """Get transactions with optional filtering."""
    query = select(Transaction)
    
    if start_date:
        query = query.where(Transaction.date >= start_date)
    if end_date:
        query = query.where(Transaction.date <= end_date)
    if category:
        query = query.where(Transaction.category == category)
    if account_id:
        query = query.where(Transaction.account_id == account_id)
    
    return list(db.scalars(query))
