#!/bin/bash
# Fix PYTHONPATH issue for PET tool

echo "Current PYTHONPATH: $PYTHONPATH"

# Unset PYTHONPATH to avoid conflicts
unset PYTHONPATH

echo "PYTHONPATH has been unset for this session"
echo "New PYTHONPATH: $PYTHONPATH"

# Verify Python environment
cd "$(dirname "$0")"
echo "---"
echo "Testing Python environment..."
./venv/bin/python -c "import sys; print('Python:', sys.executable); print('Version:', sys.version_info[:3]); print('Clean path:', all('3.11' not in p for p in sys.path))"

echo "---"
echo "You can now run: source ./venv/bin/activate && python app.py"
