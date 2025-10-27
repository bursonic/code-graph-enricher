#!/bin/bash
# Quick start script for Code Graph Enricher
# Sets up environment and runs example

set -e

echo "Code Graph Enricher - Quick Start"
echo "=================================="
echo

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo
echo "Activating virtual environment..."
source venv/bin/activate

# Install package
echo
echo "Installing code-graph-enricher..."
pip install -e . > /dev/null 2>&1
echo "✓ Package installed"

# Run example
echo
echo "Running example enrichment..."
echo
enrich-graph examples/test-code-data/.ai-gov/code-graph.json examples/test-code-data

echo
echo "=================================="
echo "Quick start complete!"
echo
echo "Next steps:"
echo "  1. View enriched graph:"
echo "     cat examples/test-code-data/.ai-gov/code-graph-enriched.json"
echo
echo "  2. View entity index:"
echo "     cat examples/test-code-data/.ai-gov/enrichment/indexes/entity-index.json"
echo
echo "  3. Try on your own code graph:"
echo "     enrich-graph /path/to/your/code-graph.json /path/to/your/source"
echo
echo "  4. Read documentation:"
echo "     cat README.md"
echo "     cat docs/ARCHITECTURE.md"
echo
