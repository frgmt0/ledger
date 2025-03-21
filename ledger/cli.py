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

from .storage import (
    get_db, create_transaction, get_transactions,
    get_or_create_category, delete_category,
    get_bank_accounts, create_bank_account
)
from .analysis import print_financial_report
from .models import Category

# Initialize colorama
init()

app = typer.Typer(help="Personal finance tracking CLI")

def interactive_menu():
    """Show interactive main menu."""
    choices = [
        Choice("Add Transaction", "add"),
        Choice("List Transactions", "list"),
        Choice("View Categories", "categories"),
        Choice("Manage Bank Accounts", "accounts"),
        Choice("Analysis", "analysis"),
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
        elif action == "accounts":
            manage_bank_accounts()
        elif action == "analysis":
            show_analysis()

def interactive_add():
    """Interactive transaction addition."""
    try:
        # First, select a bank account
        with get_db() as db:
            accounts = get_bank_accounts(db)
            if not accounts:
                typer.echo(f"{Fore.RED}No bank accounts found. Please create one first.{Style.RESET_ALL}")
                return
            
            account_choices = [
                Choice(f"{acc.name} ({acc.account_type})", acc.id)
                for acc in accounts
            ]
            account_id = questionary.select(
                "Select bank account:",
                choices=account_choices
            ).ask()
            
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
        with get_db() as db:
            # Initialize default categories if needed
            from .storage import initialize_default_categories
            initialize_default_categories(db)
            
            # Get all categories
            categories = [c.name for c in db.query(Category).all()]
            choices = [Choice(c, c) for c in sorted(categories)]
            choices.append(Choice("Add new category", "new"))
            
        category = questionary.select(
            "Select category:",
            choices=choices
        ).ask()
        
        if category == "new":
            new_category = questionary.text(
                "Enter new category name:",
                validate=lambda x: len(x) > 0
            ).ask()
            if questionary.confirm(f"Add '{new_category}' as a new category?").ask():
                category = new_category
        
        # Create the transaction
        with get_db() as db:
            transaction = create_transaction(
                db,
                date=datetime.strptime(date_str, "%Y-%m-%d"),
                description=description,
                amount=Decimal(amount),
                category=category,
                account_id=account_id,
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
                with get_db() as db:
                    categories = [c.name for c in db.query(Category).all()]
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

def manage_bank_accounts():
    """Manage bank accounts."""
    try:
        with get_db() as db:
            accounts = get_bank_accounts(db)
            
            typer.echo(f"{Fore.BLUE}Current Bank Accounts:{Style.RESET_ALL}")
            if accounts:
                for acc in accounts:
                    typer.echo(f"  - {acc.name} ({acc.account_type})")
            else:
                typer.echo("  No bank accounts configured yet")
            
            action = questionary.select(
                "Bank account management:",
                choices=[
                    Choice("Add new account", "add"),
                    Choice("Back", "back")
                ]
            ).ask()
            
            if action == "add":
                name = questionary.text(
                    "Enter account name:",
                    validate=lambda x: len(x) > 0
                ).ask()
                
                account_type = questionary.select(
                    "Select account type:",
                    choices=["Checking", "Savings", "Credit Card", "Investment"]
                ).ask()
                
                description = questionary.text(
                    "Enter description (optional):"
                ).ask()
                
                account = create_bank_account(
                    db,
                    name=name,
                    account_type=account_type,
                    description=description if description else None
                )
                
                typer.echo(
                    f"{Fore.GREEN}Bank account '{account.name}' created!{Style.RESET_ALL}"
                )
    
    except Exception as e:
        typer.echo(f"{Fore.RED}Error managing bank accounts: {str(e)}{Style.RESET_ALL}")

def show_analysis():
    """Show financial analysis and reports."""
    try:
        with get_db() as db:
            # Get filter preferences
            account_id = None
            if questionary.confirm("Filter by specific account?").ask():
                accounts = get_bank_accounts(db)
                if not accounts:
                    typer.echo(f"{Fore.RED}No bank accounts found.{Style.RESET_ALL}")
                    return
                
                account_choices = [
                    Choice(f"{acc.name} ({acc.account_type})", acc.id)
                    for acc in accounts
                ]
                account_choices.append(Choice("All Accounts", None))
                account_id = questionary.select(
                    "Select account:",
                    choices=account_choices
                ).ask()
            
            # Get date range
            start_date = None
            end_date = None
            if questionary.confirm("Filter by date range?").ask():
                start_date = questionary.text(
                    "Enter start date (YYYY-MM-DD):",
                    validate=lambda x: len(x) == 0 or len(x) == 10
                ).ask()
                end_date = questionary.text(
                    "Enter end date (YYYY-MM-DD):",
                    validate=lambda x: len(x) == 0 or len(x) == 10
                ).ask()
            
            # Convert dates if provided
            if start_date:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Generate and print report
            print_financial_report(db, start_date, end_date, account_id)
    
    except Exception as e:
        typer.echo(f"{Fore.RED}Error generating analysis: {str(e)}{Style.RESET_ALL}")

def show_categories():
    """Display available categories and allow management."""
    try:
        with get_db() as db:
            from .models import Category
            from .storage import DEFAULT_CATEGORIES, initialize_database
            
            # Ensure database and default categories are initialized
            initialize_database()
            
            categories = db.query(Category).order_by(Category.name).all()
            
            typer.echo(f"{Fore.BLUE}Available Categories:{Style.RESET_ALL}")
            if categories:
                for category in categories:
                    is_default = category.name in DEFAULT_CATEGORIES
                    category_text = f"  - {category.name}"
                    if is_default:
                        category_text += f" {Fore.YELLOW}(default){Style.RESET_ALL}"
                    typer.echo(category_text)
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
    amount: float = typer.Argument(..., help="Transaction amount"),
    description: str = typer.Option(..., help="Transaction description"),
    category: Optional[str] = typer.Option(None, help="Transaction category"),
    date: str = typer.Option(
        datetime.now().strftime("%Y-%m-%d"),
        help="Transaction date (YYYY-MM-DD)",
    ),
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
