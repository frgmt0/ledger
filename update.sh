#!/bin/zsh

echo "Updating Ledger CLI..."

# Activate virtual environment
source .venv/bin/activate

# Pull latest changes
echo "Pulling latest changes..."
git pull

# Backup database
echo "Backing up database..."
cp ~/.ledger/ledger.db ~/.ledger/ledger.db.backup

# Reinstall dependencies
echo "Reinstalling dependencies..."
pip install -e ".[dev]"

# Run migrations
echo "Running database migrations..."
alembic upgrade head

echo "Update complete! You can now run the updated version."
echo "Your previous database has been backed up to: ~/.ledger/ledger.db.backup"
