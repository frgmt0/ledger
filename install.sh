#!/bin/zsh

echo "Installing Ledger CLI..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -e ".[dev]"

# Initialize database
echo "Initializing database..."
alembic upgrade head

# Make the CLI executable
chmod +x .venv/bin/ledger

echo "Installation complete! You can now run 'ledger' command."
echo "To get started, run: ledger"
