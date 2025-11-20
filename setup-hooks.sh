#!/bin/bash
# Setup git hooks for the project

echo "📋 Setting up git hooks..."

# Create .git/hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy pre-commit hook
cp .git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "✅ Git hooks installed successfully!"
echo ""
echo "The pre-commit hook will remind you to keep database schema synchronized."
echo "See backend/DATABASE_SCHEMA.md for details."
