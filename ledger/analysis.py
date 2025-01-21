"""
Analysis module for generating financial reports and visualizations.
"""
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import func
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.progress import track

from .models import Transaction, BankAccount
from .storage import get_transactions

console = Console()

def get_account_balance(
    db: Session,
    account_id: Optional[int] = None,
    end_date: Optional[datetime] = None
) -> Decimal:
    """Calculate account balance up to given date."""
    query = db.query(func.sum(Transaction.amount))
    
    if account_id is not None:
        query = query.filter(Transaction.account_id == account_id)
    if end_date is not None:
        query = query.filter(Transaction.date <= end_date)
        
    result = query.scalar()
    return Decimal('0') if result is None else result

def get_category_summary(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    account_id: Optional[int] = None
) -> Dict[str, Decimal]:
    """Get spending summary by category."""
    transactions = get_transactions(db, start_date, end_date, account_id=account_id)
    
    summary = defaultdict(Decimal)
    for t in transactions:
        category = t.category or "Uncategorized"
        summary[category] += t.amount
        
    return dict(summary)

def generate_ascii_bar_chart(
    data: Dict[str, Decimal],
    width: int = 40,
    show_positive: bool = True
) -> str:
    """Generate ASCII bar chart from data."""
    if not data:
        return "No data available"
        
    # Filter positive/negative values based on show_positive
    filtered_data = {k: v for k, v in data.items() 
                    if (v >= 0) == show_positive}
    
    if not filtered_data:
        return "No data available"
    
    # Find maximum absolute value for scaling
    max_val = max(abs(v) for v in filtered_data.values())
    
    # Generate bars
    output = []
    for category, amount in sorted(filtered_data.items(), 
                                 key=lambda x: abs(x[1]), 
                                 reverse=True):
        bar_length = int(abs(amount) / max_val * width)
        bar = '█' * bar_length
        amount_str = f"${abs(amount):,.2f}"
        output.append(f"{category:20} {amount_str:>10} {bar}")
    
    return "\n".join(output)

def print_financial_report(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    account_id: Optional[int] = None
):
    """Print comprehensive financial report."""
    # Get account info if specified
    account_name = "All Accounts"
    if account_id is not None:
        account = db.query(BankAccount).filter_by(id=account_id).first()
        if account:
            account_name = f"{account.name} ({account.account_type})"
    
    # Calculate balances and summaries
    balance = get_account_balance(db, account_id, end_date)
    category_summary = get_category_summary(db, start_date, end_date, account_id)
    
    # Print report header
    console.print(f"\n[bold blue]Financial Report - {account_name}[/bold blue]")
    if start_date:
        console.print(f"From: {start_date.strftime('%Y-%m-%d')}")
    if end_date:
        console.print(f"To: {end_date.strftime('%Y-%m-%d')}")
    console.print(f"\nCurrent Balance: [{'green' if balance >= 0 else 'red'}]${abs(balance):,.2f}[/]")
    
    # Print income summary
    console.print("\n[bold green]Income Summary:[/bold green]")
    income_chart = generate_ascii_bar_chart(category_summary, show_positive=True)
    console.print(income_chart)
    
    # Print expense summary
    console.print("\n[bold red]Expense Summary:[/bold red]")
    expense_chart = generate_ascii_bar_chart(category_summary, show_positive=False)
    console.print(expense_chart)
