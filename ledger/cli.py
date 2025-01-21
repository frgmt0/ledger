"""
CLI interface for the ledger application.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

import typer
from colorama import init, Fore, Style

from .storage import get_db, create_transaction, get_transactions

# Initialize colorama
init()

app = typer.Typer(help="Personal finance tracking CLI")


@app.command()
def add(
    date: str = typer.Option(
        datetime.now().strftime("%Y-%m-%d"),
        help="Transaction date (YYYY-MM-DD)",
    ),
    description: str = typer.Option(..., help="Transaction description"),
    amount: float = typer.Option(..., help="Transaction amount"),
    category: Optional[str] = typer.Option(None, help="Transaction category"),
    notes: Optional[str] = typer.Option(None, help="Additional notes"),
):
    """Add a new transaction."""
    try:
        transaction = create_transaction(
            date=datetime.strptime(date, "%Y-%m-%d"),
            description=description,
            amount=Decimal(str(amount)),
            category=category,
            notes=notes,
        )
        typer.echo(
            f"{Fore.GREEN}Transaction added successfully: "
            f"{transaction.description} (${transaction.amount}){Style.RESET_ALL}"
        )
    except Exception as e:
        typer.echo(f"{Fore.RED}Error adding transaction: {str(e)}{Style.RESET_ALL}")
        raise typer.Exit(1)


@app.command()
def list(
    start_date: Optional[str] = typer.Option(
        None, help="Start date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = typer.Option(
        None, help="End date (YYYY-MM-DD)"
    ),
    category: Optional[str] = typer.Option(
        None, help="Filter by category"
    ),
):
    """List transactions with optional filtering."""
    try:
        with get_db() as db:
            transactions = get_transactions(
                db,
                start_date=datetime.strptime(start_date, "%Y-%m-%d") if start_date else None,
                end_date=datetime.strptime(end_date, "%Y-%m-%d") if end_date else None,
                category=category,
            )
            
            if not transactions:
                typer.echo(f"{Fore.YELLOW}No transactions found.{Style.RESET_ALL}")
                return
            
            for t in transactions:
                typer.echo(
                    f"{Fore.BLUE}{t.date.strftime('%Y-%m-%d')} | "
                    f"{t.description} | "
                    f"{Fore.GREEN if t.amount >= 0 else Fore.RED}"
                    f"${abs(t.amount)}{Style.RESET_ALL}"
                    f"{f' | {t.category}' if t.category else ''}"
                )
    
    except Exception as e:
        typer.echo(f"{Fore.RED}Error listing transactions: {str(e)}{Style.RESET_ALL}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
