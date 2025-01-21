#!/bin/zsh

echo "Installing Ledger CLI globally..."

# Install package globally
echo "Installing dependencies..."
pip3 install -e ".[dev]"

# Initialize database
echo "Initializing database..."
alembic upgrade head

echo "Installation complete! You can now run 'ledger' command from anywhere."
echo "To get started, run: ledger"
