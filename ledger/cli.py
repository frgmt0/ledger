"""
CLI interface for the ledger application.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
import questionary
from questionary import Choice

import typer
from colorama import init, Fore, Style

from .storage import get_db, create_transaction, get_transactions
from .categories import Category

# Initialize colorama
init()

app = typer.Typer(help="Personal finance tracking CLI")

def interactive_menu():
    """Show interactive main menu."""
    choices = [
        Choice("Add Transaction", "add"),
        Choice("List Transactions", "list"),
        Choice("View Categories", "categories"),
        Choice("Exit", "exit")
    ]
    
    while True:
        action = questionary.select(
            "What would you like to do?",
            choices=choices
        ).ask()
        
        if action == "exit":
            break
        elif action == "add":
            interactive_add()
        elif action == "list":
            interactive_list()
        elif action == "categories":
            show_categories()

def interactive_add():
    """Interactive transaction addition."""
    try:
        # Get transaction details interactively
        date_str = questionary.text(
            "Enter date (YYYY-MM-DD):",
            default=datetime.now().strftime("%Y-%m-%d")
        ).ask()
        
        description = questionary.text(
            "Enter description:",
            validate=lambda x: len(x) > 0
        ).ask()
        
        amount = questionary.text(
            "Enter amount (negative for expenses):",
            validate=lambda x: x.replace(".", "").replace("-", "").isdigit()
        ).ask()
        
        # Show category selection with existing categories
        categories = [c.value for c in Category]
        category = questionary.select(
            "Select category:",
            choices=categories + ["Add new category"]
        ).ask()
        
        if category == "Add new category":
            new_category = questionary.text(
                "Enter new category name:",
                validate=lambda x: len(x) > 0
            ).ask()
            if questionary.confirm(f"Add '{new_category}' as a new category?").ask():
                # In a real implementation, you would add this to the Category enum
                category = new_category
        
        # Create the transaction
        with get_db() as db:
            transaction = create_transaction(
                db,
                date=datetime.strptime(date_str, "%Y-%m-%d"),
                description=description,
                amount=Decimal(amount),
                category=category,
            )
            
        typer.echo(
            f"{Fore.GREEN}Transaction added successfully: "
            f"{transaction.description} (${transaction.amount}){Style.RESET_ALL}"
        )
    
    except Exception as e:
        typer.echo(f"{Fore.RED}Error adding transaction: {str(e)}{Style.RESET_ALL}")

def interactive_list():
    """Interactive transaction listing."""
    try:
        use_filters = questionary.confirm("Do you want to use filters?").ask()
        
        start_date = None
        end_date = None
        category = None
        
        if use_filters:
            if questionary.confirm("Filter by date range?").ask():
                start_date = questionary.text(
                    "Enter start date (YYYY-MM-DD):"
                ).ask()
                end_date = questionary.text(
                    "Enter end date (YYYY-MM-DD):"
                ).ask()
            
            if questionary.confirm("Filter by category?").ask():
                categories = [c.value for c in Category]
                category = questionary.select(
                    "Select category:",
                    choices=categories
                ).ask()
        
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

def show_categories():
    """Display available categories and allow management."""
    try:
        with get_db() as db:
            from .models import Category
            from .storage import DEFAULT_CATEGORIES
            categories = db.query(Category).order_by(Category.name).all()
            
            typer.echo(f"{Fore.BLUE}Available Categories:{Style.RESET_ALL}")
            if categories:
                for category in categories:
                    is_default = category.name in DEFAULT_CATEGORIES
                    typer.echo(
                        f"  - {category.name} "
                        f"{Fore.YELLOW}(default){Style.RESET_ALL}" if is_default else ""
                    )
            else:
                typer.echo("  No categories defined yet")
            
            # Category management options
            action = questionary.select(
                "Category management:",
                choices=[
                    Choice("Add new category", "add"),
                    Choice("Delete custom category", "delete"),
                    Choice("Back", "back")
                ]
            ).ask()
            
            if action == "add":
                new_category = questionary.text(
                    "Enter new category name:",
                    validate=lambda x: len(x) > 0
                ).ask()
                get_or_create_category(db, new_category)
                typer.echo(f"{Fore.GREEN}Category '{new_category}' added!{Style.RESET_ALL}")
            
            elif action == "delete":
                custom_categories = [
                    c.name for c in categories 
                    if c.name not in DEFAULT_CATEGORIES
                ]
                if not custom_categories:
                    typer.echo(f"{Fore.YELLOW}No custom categories to delete{Style.RESET_ALL}")
                    return
                
                to_delete = questionary.select(
                    "Select category to delete:",
                    choices=custom_categories + ["Cancel"]
                ).ask()
                
                if to_delete != "Cancel":
                    if delete_category(db, to_delete):
                        typer.echo(f"{Fore.GREEN}Category '{to_delete}' deleted!{Style.RESET_ALL}")
                    else:
                        typer.echo(f"{Fore.RED}Could not delete category{Style.RESET_ALL}")
                        
    except Exception as e:
        typer.echo(f"{Fore.RED}Error managing categories: {str(e)}{Style.RESET_ALL}")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Personal finance tracking CLI."""
    if ctx.invoked_subcommand is None:
        interactive_menu()

@app.command()
def add(
    date: str = typer.Option(
        datetime.now().strftime("%Y-%m-%d"),
        help="Transaction date (YYYY-MM-DD)",
    ),
    description: str = typer.Option(..., help="Transaction description"),
    amount: float = typer.Option(..., help="Transaction amount"),
    category: Optional[str] = typer.Option(None, help="Transaction category"),
):
    """Add a new transaction."""
    try:
        with get_db() as db:
            transaction = create_transaction(
                db,
                date=datetime.strptime(date, "%Y-%m-%d"),
                description=description,
                amount=Decimal(str(amount)),
                category=category,
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
