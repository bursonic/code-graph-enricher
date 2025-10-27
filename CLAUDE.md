# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Code Graph Enricher is a tool for iterative enrichment of code graphs with structural, semantic, and domain knowledge. It takes a basic code graph (JSON format with nodes and edges) and progressively enriches it through three analysis layers that build upon each other.

## Development Commands

### Installation & Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in editable mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### Running the Tool
```bash
# Basic usage
enrich-graph <graph_json_path> [root_code_path]

# With options
enrich-graph ./code-graph.json ./src --iterations 3
enrich-graph ./code-graph.json ./src --no-convergence
```

### Development Tools
```bash
# Run tests (when tests/ directory is populated)
pytest tests/

# Code formatting
black src/enricher/

# Linting
flake8 src/enricher/

# Type checking
mypy src/enricher/
```

## Architecture

### Core Design Pattern: Iterative Multi-Layer Enrichment

The architecture follows a pipeline pattern where enrichment happens in **iterations**, with each iteration running all three layers sequentially. This allows layers to refine their analysis based on previous iterations' results.

**Iteration Flow:**
```
Iteration 1:
  Layer 1 (Structural) → Initial classification
  Layer 2 (Semantic)   → Pattern detection using Layer 1
  Layer 3 (Domain)     → Domain extraction using Layers 1 & 2

Iteration 2:
  Layer 1 → Refine classifications with more context
  Layer 2 → Refine patterns with validated data
  Layer 3 → Validate relationships, increase confidence

Convergence check → Stop if no changes
```

### Key Components

**IterativeEnricher** (`src/enricher/iterative_enricher.py`)
- Orchestrates the entire enrichment pipeline
- Manages iteration lifecycle and convergence detection
- Saves intermediate artifacts after each layer
- Uses MD5 hash of enrichment data to detect convergence
- Stores layer history in `self.layers` list for context-aware analysis

**EnricherPass** (abstract base class in `iterative_enricher.py`)
- Base class for all enrichment layers
- Subclasses must implement `enrich_node()` and `enrich_edge()`
- Each pass has a `layer_num` and `name` identifier
- The `process()` method orchestrates node/edge enrichment

**Three Enrichment Layers:**

1. **StructuralEnricher** (`layer1_structural.py`)
   - Classifies nodes as domain/infrastructure/unknown
   - Calculates complexity metrics (LOC, nesting depth, parameters, methods)
   - Analyzes dependencies (import depth, import counts)
   - Uses heuristic patterns for classification (e.g., 'user', 'product' = domain; 'config', 'utils' = infrastructure)

2. **SemanticEnricher** (`layer2_semantic.py`)
   - Detects design patterns (Entity, Service, Repository, Factory, DTO, ValueObject)
   - Analyzes naming conventions (snake_case, camelCase, PascalCase)
   - Classifies method roles (getter, setter, validator, calculator, etc.)
   - Determines API surface (public/private/protected)
   - Builds on Layer 1 classifications

3. **DomainEnricher** (`layer3_domain.py`)
   - Extracts domain concept names from entities
   - Identifies business rules (validation, calculation, constraints)
   - Detects workflow participation (authentication, checkout, payment, etc.)
   - Infers entity relationships (HAS_MANY, HAS_ONE, USES, CREATES, DEPENDS_ON)
   - Uses both Layer 1 and Layer 2 enrichments

### Data Flow

1. **Input**: Code graph JSON with nodes (files/classes/functions) and edges (contains/imports/calls/inherits)
2. **Processing**: Each enricher adds an `enrichment.layerN` key to nodes/edges
3. **Output**:
   - `code-graph-enriched.json` - Final enriched graph
   - `enrichment/l1-structural.json`, `l2-semantic.json`, `l3-domain.json` - Intermediate layers
   - `enrichment/indexes/entity-index.json` - Fast lookup index

### Context Propagation

Enrichers receive a `context` parameter (list of previous iteration graphs) allowing them to:
- Cross-validate findings from previous iterations
- Refine initial guesses with more information
- Build confidence through multiple signals
- Discover indirect relationships

## Adding New Enrichment Layers

To extend the system with Layer 4:

```python
from enricher import EnricherPass

class Layer4CustomEnricher(EnricherPass):
    def __init__(self):
        super().__init__(layer_num=4, name="custom")

    def enrich_node(self, node, graph, context):
        # Access previous layers
        layer3 = node.get('enrichment', {}).get('layer3', {})

        # Your analysis logic
        return {
            "custom_metric": 42,
            "custom_data": []
        }

    def enrich_edge(self, edge, graph, context):
        return {}
```

Register in CLI (`cli.py`):
```python
from .layer4_custom import Layer4CustomEnricher
enricher.add_enricher(Layer4CustomEnricher())
```

## Customization Points

**Classification Heuristics** (`layer1_structural.py:_classify_by_name()`)
- Modify `infra_patterns` and `domain_patterns` lists for domain-specific keywords

**Pattern Detection** (`layer2_semantic.py:_detect_patterns()`)
- Add new pattern detection logic based on naming and structure

**Domain Keywords** (`layer3_domain.py:_extract_domain_concepts()`)
- Extend `domain_keywords` list for your specific domain

**Workflow Patterns** (`layer3_domain.py:_detect_workflow_participation()`)
- Add custom workflows to `workflow_patterns` dictionary

## Important Implementation Details

- **No external dependencies**: Uses only Python stdlib for maximum portability
- **Deep copying**: Uses `json.loads(json.dumps(obj))` for graph cloning
- **Convergence detection**: MD5 hash of enrichment data only (ignores base graph)
- **File reading**: Layer 1 attempts to read source files from `root_path` for LOC metrics
- **Default iterations**: CLI defaults to 2 iterations (can be changed with `--iterations`)
- **Output location**: Enriched files saved in same directory as input graph file

## Input/Output Formats

**Expected Input Structure:**
```json
{
  "nodes": [
    {
      "id": "unique-id",
      "type": "file|class|function",
      "name": "NodeName",
      "path": "relative/path/to/file.py",
      "location": {"line": 10, "column": 4},
      "metadata": {}
    }
  ],
  "edges": [
    {
      "source": "node-id",
      "target": "node-id",
      "type": "contains|imports|calls|inherits"
    }
  ]
}
```

**Output Enrichment Structure:**
Each node gains an `enrichment` key with layer1, layer2, layer3 sub-keys containing that layer's analysis results.
