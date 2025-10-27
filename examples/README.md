# Examples

This directory contains example code graphs and usage demonstrations.

## test-code-data

A simple Python e-commerce application with:
- `models.py` - User, Product, ShoppingCart classes
- `utils.py` - Utility functions and DataProcessor
- `main.py` - Application entry point

The `.ai-gov/` directory contains:
- `code-graph.json` - Base code graph (input)
- `code-graph-enriched.json` - Enriched output (after running enricher)
- `enrichment/` - Intermediate layer artifacts

## Running the Example

```bash
# From the code-graph-enricher root directory

# Install the tool
pip install -e .

# Run enrichment on the example
enrich-graph examples/test-code-data/.ai-gov/code-graph.json examples/test-code-data

# View results
cat examples/test-code-data/.ai-gov/code-graph-enriched.json

# View entity index
cat examples/test-code-data/.ai-gov/enrichment/indexes/entity-index.json
```

## Expected Results

The enricher should detect:
- **2 Entity patterns**: User, Product
- **Domain classifications**: User, Product, ShoppingCart
- **Infrastructure classifications**: main, initialize_app
- **Method roles**: Getters (get_display_name), calculators (calculate_total), validators (is_adult)
- **Domain concepts**: User, Product, Cart, Order, Item

## Creating Your Own Example

1. Generate a code graph for your project using a tree-sitter parser or similar tool
2. Ensure it follows the input format (see README.md)
3. Run the enricher:
   ```bash
   enrich-graph /path/to/your/code-graph.json /path/to/your/source
   ```
4. Inspect the results in the enrichment/ directory
