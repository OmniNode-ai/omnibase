#!/bin/bash
# Refactor Mode - Manual Quality Commands
# Run these when you want quick quality checks (optional during refactor)

quick-lint() {
    echo "🔍 Running quick lint..."
    poetry run ruff src/ --fix
}

quick-format() {
    echo "🎨 Running quick format..."
    poetry run black src/
}

quick-validate() {
    echo "✅ Running quick validation..."
    poetry run onex run parity_validator_node --args='["--format", "summary"]'
}

quick-test() {
    echo "🧪 Running quick tests..."
    poetry run pytest -x --tb=short
}

quick-all() {
    echo "🚀 Running all quick checks..."
    quick-lint && quick-format && quick-validate
    echo "✅ Quick validation complete"
}

# Usage:
# source refactor_tools.sh
# quick-lint    # Fix linting issues
# quick-format  # Format code
# quick-validate # Quick parity check
# quick-test    # Fast test run
# quick-all     # Run lint + format + validate 