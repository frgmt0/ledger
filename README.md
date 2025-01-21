# Ledger - A Personal CLI Finance Tool

A simple but powerful command-line ledger system for tracking personal finances with an easy input interface.

## Features

- Transaction recording with amount, category, date, and description
- Transaction querying and filtering
- Monthly/yearly financial summaries
- Category-based analysis
- Data export capabilities

## Installation

Requires Python 3.8+

### Global Installation
```bash
./install.sh
```

This will install the `ledger` command globally on your system.

### Development Installation
For development in a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

Basic commands:

```bash
# Add a transaction
ledger add 42.50 --category food --description "Groceries"

# List transactions
ledger list --category food --start-date 2024-01-01

# View summary
ledger summary --period monthly

# Manage categories
ledger categories list
ledger categories add food
ledger categories remove food

# Export data
ledger export --format csv
```

## Development

This project follows:
- PEP 8 style guide
- Type hints throughout
- Comprehensive docstrings
- Test-driven development

### Running Tests

```bash
pytest
```

### Type Checking

```bash
mypy finance_cli
```

## License

MIT License
