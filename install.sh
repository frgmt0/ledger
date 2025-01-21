#!/bin/zsh

echo "Installing Ledger CLI globally..."

# Check if pipx is installed
if ! command -v pipx &> /dev/null; then
    echo "Installing pipx..."
    brew install pipx
    pipx ensurepath
fi

# Install package globally using pipx
echo "Installing package..."
pipx install -e .

# Initialize database if it doesn't exist
echo "Initializing database..."
if [ ! -f ~/.ledger/ledger.db ]; then
    mkdir -p ~/.ledger
    alembic upgrade head
else
    echo "Database already exists, skipping initialization"
fi

echo "Installation complete! You can now run 'ledger' command from anywhere."
echo "To get started, run: ledger"
