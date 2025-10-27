# Code Graph Enricher

A powerful tool for iterative enrichment of code graphs with structural, semantic, and domain knowledge. Progressively extracts deeper insights through multiple analysis layers that build upon each other.

## Overview

Code Graph Enricher takes a basic code graph (nodes and edges representing files, classes, functions, and their relationships) and enriches it with:

- **Structural knowledge**: Classification, complexity metrics, dependencies
- **Semantic knowledge**: Design patterns, naming conventions, method roles
- **Domain knowledge**: Business entities, rules, workflows, relationships

The enrichment is **iterative** - each layer uses results from previous layers to refine and validate its analysis, creating progressively deeper understanding.

## Features

✨ **Multi-Layer Enrichment**
- Layer 1: Structural analysis (classification, complexity, dependencies)
- Layer 2: Semantic analysis (patterns, naming, roles)
- Layer 3: Domain extraction (entities, business rules, workflows)

🔄 **Iterative Refinement**
- Multiple passes where each iteration refines previous results
- Automatic convergence detection
- Context-aware analysis using previous layer results

📦 **Intermediate Artifacts**
- Saves each layer separately for debugging and inspection
- Generates fast-lookup indexes
- Preserves enrichment history

📊 **Rich Statistics**
- Node classifications (domain vs infrastructure)
- Pattern detection counts
- Coverage reports

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Install from Source

```bash
# Clone or extract the repository
cd code-graph-enricher

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Quick Start

```bash
# 1. Generate a base code graph (using tree-sitter or similar tool)
# This should produce a code-graph.json file

# 2. Enrich the graph
enrich-graph path/to/code-graph.json path/to/source/code

# 3. View results
cat path/to/code-graph-enriched.json
```

## Usage

### Basic Usage

```bash
enrich-graph <graph_json_path> [root_code_path]
```

**Arguments:**
- `graph_json_path` - Path to the input code graph JSON file
- `root_code_path` - (Optional) Root directory of the source code

**Example:**
```bash
enrich-graph ./myproject/.ai-gov/code-graph.json ./myproject/src
```

### Advanced Options

```bash
# Custom number of iterations
enrich-graph code-graph.json ./src --iterations 3

# Disable convergence check (always run max iterations)
enrich-graph code-graph.json ./src --no-convergence

# Combined
enrich-graph code-graph.json ./src --iterations 4 --no-convergence
```

## Input Format

The tool expects a code graph in JSON format with this structure:

```json
{
  "nodes": [
    {
      "id": "unique-id",
      "type": "file|class|function",
      "name": "FileName",
      "path": "relative/path",
      "location": {"line": 0, "column": 0},
      "metadata": {}
    }
  ],
  "edges": [
    {
      "source": "node-id",
      "target": "node-id",
      "type": "contains|imports|calls|inherits"
    }
  ],
  "metadata": {}
}
```

You can generate this format using tools like:
- tree-sitter-based parsers
- Language-specific AST tools
- Custom code analysis tools

## Output Structure

The enricher creates the following output:

```
output-directory/
├── code-graph-enriched.json    # Final enriched graph
└── enrichment/
    ├── l1-structural.json      # After Layer 1
    ├── l2-semantic.json        # After Layer 2
    ├── l3-domain.json          # After Layer 3
    └── indexes/
        └── entity-index.json   # Fast entity lookup
```

### Enriched Node Structure

Each node in the enriched graph contains an `enrichment` key:

```json
{
  "id": "...",
  "name": "User",
  "type": "class",
  "enrichment": {
    "layer1": {
      "classification": "domain",
      "complexity": {
        "loc": 50,
        "nesting_depth": 2,
        "num_methods": 5
      },
      "dependencies": {
        "import_depth": 1,
        "num_imports": 3,
        "imports_from": ["typing", "dataclasses"]
      }
    },
    "layer2": {
      "patterns": ["Entity", "ValueObject"],
      "naming_analysis": {
        "terms": ["user"],
        "conventions": "PascalCase",
        "role_indicators": []
      },
      "method_roles": [],
      "api_surface": "public"
    },
    "layer3": {
      "domain_concepts": ["User"],
      "business_rules": [],
      "workflow_participation": ["authentication", "registration"],
      "entity_relationships": [
        {
          "type": "HAS_MANY",
          "target": "Order",
          "inferred_from": "User.get_orders"
        }
      ]
    }
  }
}
```

## Enrichment Layers Explained

### Layer 1: Structural Enrichment

**What it does:**
- Classifies code as domain vs infrastructure
- Calculates complexity metrics
- Analyzes dependencies and import chains

**Classification heuristics:**
- Domain: User, Product, Order, Service, Repository
- Infrastructure: config, utils, setup, main, test

### Layer 2: Semantic Enrichment

**What it does:**
- Detects design patterns (Entity, Service, Repository, Factory, etc.)
- Analyzes naming conventions (snake_case, camelCase, PascalCase)
- Classifies method roles (getter, setter, validator, calculator, etc.)
- Determines API surface (public, private, protected)

**Detected patterns:**
- Entity, ValueObject, Service, Repository, Factory, DTO

### Layer 3: Domain Enrichment

**What it does:**
- Extracts domain concept names
- Identifies business rules and validation logic
- Detects workflow participation
- Infers entity relationships

**Relationship types:**
- HAS_MANY, HAS_ONE, USES, CREATES, DEPENDS_ON

## How Iteration Works

The enricher runs multiple iterations, where each iteration applies all three layers in sequence:

```
Iteration 1:
  Layer 1 → Classify nodes based on names
  Layer 2 → Detect patterns using Layer 1 classifications
  Layer 3 → Extract domain knowledge using Layer 1 & 2

Iteration 2:
  Layer 1 → Refine classifications with more context
  Layer 2 → Refine patterns with validated data
  Layer 3 → Validate relationships, increase confidence

Convergence check → If no changes, stop early
```

This allows layers to:
- Cross-validate findings
- Refine initial guesses
- Build confidence through multiple signals
- Discover indirect relationships

## Examples

### Python E-commerce Application

```bash
# Enrich a Python e-commerce codebase
enrich-graph ./ecommerce/.ai-gov/code-graph.json ./ecommerce/src

# Results:
# - User, Product, Order detected as Entities
# - ShoppingCart.checkout() identified in checkout workflow
# - calculate_discount() identified as business rule
# - User HAS_MANY Order relationship inferred
```

### Viewing Specific Entity

```python
import json

with open('code-graph-enriched.json') as f:
    graph = json.load(f)

# Find User entity
user = next(n for n in graph['nodes'] if n['name'] == 'User')
print(json.dumps(user['enrichment'], indent=2))
```

### Using Indexes

```bash
# Quick lookup of all entities
cat enrichment/indexes/entity-index.json | \
  jq '[.[] | select(.patterns[] == "Entity") | .name]'
```

## Extending the Enricher

### Adding a New Layer

Create a new enricher class:

```python
from enricher import EnricherPass

class Layer4CustomEnricher(EnricherPass):
    def __init__(self):
        super().__init__(layer_num=4, name="custom")

    def enrich_node(self, node, graph, context):
        # Your custom analysis
        return {
            "custom_metric": 42,
            "custom_data": []
        }

    def enrich_edge(self, edge, graph, context):
        return {}
```

Use it in the CLI or programmatically:

```python
from enricher import IterativeEnricher
from my_layers import Layer4CustomEnricher

enricher = IterativeEnricher(graph, output_dir)
enricher.add_enricher(Layer4CustomEnricher())
result = enricher.enrich()
```

### Customizing Classification

Edit `src/enricher/layer1_structural.py`:

```python
def _classify_by_name(self, name: str, node_type: str) -> str:
    # Add your domain-specific patterns
    if 'widget' in name.lower():
        return 'domain'
    # ... rest of logic
```

## Troubleshooting

**Issue: Virtual environment not found**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Issue: Graph file not found**
- Ensure you've generated the base code graph first
- Check the file path is correct

**Issue: Poor classification results**
- Adjust heuristics in layer1_structural.py
- Add your domain-specific keywords
- Increase iterations for more refinement

**Issue: Missing patterns**
- Check naming conventions match expected patterns
- Review layer2_semantic.py pattern detection rules

## Development

### Running Tests

```bash
pytest tests/
```

### Code Structure

```
code-graph-enricher/
├── src/enricher/          # Main package
│   ├── __init__.py
│   ├── cli.py             # CLI entry point
│   ├── iterative_enricher.py    # Core orchestrator
│   ├── layer1_structural.py     # Layer 1
│   ├── layer2_semantic.py       # Layer 2
│   ├── layer3_domain.py         # Layer 3
│   └── enrichment_schemas.py    # Schema definitions
├── tests/                 # Test suite
├── examples/              # Example code graphs
└── docs/                  # Additional documentation
```

## Contributing

Contributions welcome! Areas for improvement:
- Support for more programming languages
- Additional design pattern detection
- Machine learning-based classification
- Better relationship inference
- Visualization tools

## License

[Specify your license here]

## Acknowledgments

Built for extracting domain knowledge from codebases to assist AI-powered development tools.

## Support

- Issues: [GitHub Issues](https://github.com/yourusername/code-graph-enricher/issues)
- Documentation: See `docs/` directory
- Examples: See `examples/` directory
