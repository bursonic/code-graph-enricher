# Architecture

## Overview

Code Graph Enricher uses a **layered, iterative architecture** where each layer builds upon previous layers to progressively extract deeper knowledge from code graphs.

## Core Components

### 1. IterativeEnricher (Orchestrator)

**Location**: `src/enricher/iterative_enricher.py`

**Responsibilities**:
- Manages the enrichment pipeline
- Coordinates multiple enricher passes
- Handles iteration and convergence detection
- Saves intermediate artifacts
- Generates indexes and statistics

**Key Methods**:
- `add_enricher(enricher)` - Register an enrichment layer
- `enrich(max_iterations, convergence_check)` - Run the pipeline
- `get_statistics(graph)` - Compute enrichment stats

### 2. EnricherPass (Base Class)

**Location**: `src/enricher/iterative_enricher.py`

**Purpose**: Abstract base for all enrichment layers

**Interface**:
```python
class EnricherPass(ABC):
    def __init__(self, layer_num: int, name: str)

    @abstractmethod
    def enrich_node(self, node, graph, context) -> Dict

    @abstractmethod
    def enrich_edge(self, edge, graph, context) -> Dict

    def process(self, graph, context) -> Dict
```

**Contract**:
- Each pass receives the full graph
- Context contains all previous iteration results
- Returns enrichment metadata to add to nodes/edges

### 3. Layer Implementations

#### Layer 1: StructuralEnricher

**Location**: `src/enricher/layer1_structural.py`

**Purpose**: Basic structural analysis

**Extracts**:
- Classification (domain vs infrastructure)
- Complexity metrics (LOC, nesting depth)
- Dependency information (imports, depth)

**Key Algorithms**:
- Name-based classification
- Import-based classification
- File reading for complexity calculation

#### Layer 2: SemanticEnricher

**Location**: `src/enricher/layer2_semantic.py`

**Purpose**: Pattern detection and naming analysis

**Extracts**:
- Design patterns (Entity, Service, Repository, etc.)
- Naming conventions (snake_case, camelCase, PascalCase)
- Method roles (getter, setter, validator, etc.)
- API surface (public/private/protected)

**Key Algorithms**:
- Pattern matching on class names
- Camel/snake case splitting
- Role prefix detection

#### Layer 3: DomainEnricher

**Location**: `src/enricher/layer3_domain.py`

**Purpose**: Domain knowledge extraction

**Extracts**:
- Domain concepts (entity names)
- Business rules (validators, calculators)
- Workflow participation
- Entity relationships (HAS_MANY, HAS_ONE, USES)

**Key Algorithms**:
- Pattern-based concept extraction
- Method signature analysis for relationships
- Workflow keyword detection

## Data Flow

```
Input: code-graph.json
   ↓
IterativeEnricher.enrich()
   ↓
┌─────────────────────────────┐
│  Iteration 1                │
│  ┌─────────────────────┐   │
│  │ Layer 1 (Structural)│   │
│  └──────────┬──────────┘   │
│             ↓               │
│  ┌─────────────────────┐   │
│  │ Layer 2 (Semantic)  │   │
│  │ (uses Layer 1)      │   │
│  └──────────┬──────────┘   │
│             ↓               │
│  ┌─────────────────────┐   │
│  │ Layer 3 (Domain)    │   │
│  │ (uses Layer 1 & 2)  │   │
│  └──────────┬──────────┘   │
│             ↓               │
│    Save: l1, l2, l3.json   │
└─────────────┬───────────────┘
              ↓
        Convergence?
              ↓
         Yes / No
              ↓
        If No: Iteration 2
              ↓
┌─────────────────────────────┐
│  Iteration 2                │
│  (same layers, more context)│
└─────────────┬───────────────┘
              ↓
    Generate indexes
              ↓
Output: code-graph-enriched.json
        + enrichment/ artifacts
```

## Iteration & Convergence

### Why Iterate?

1. **Cross-validation**: Multiple signals confirm findings
2. **Indirect relationships**: Layer 3 can discover connections Layer 2 prepared
3. **Refinement**: Initial guesses improved with context
4. **Confidence**: Repeated detection increases certainty

### Convergence Detection

The enricher computes a hash of all enrichment data after each iteration:

```python
hash = MD5(json.dumps(all_enrichments, sorted=True))
```

If the hash is unchanged from the previous iteration, convergence is achieved and the pipeline stops early.

### Context Passing

Each layer receives `context` - a list of all previous full graph states:

```python
context = [
    iteration_1_graph,
    iteration_2_graph,
    ...
]
```

Layers can access previous iterations to:
- Validate findings
- Track changes
- Build confidence scores
- Cross-reference data

## File Storage Strategy

### Intermediate Artifacts

Each layer is saved separately:

```
enrichment/
├── l1-structural.json    # Graph after Layer 1
├── l2-semantic.json      # Graph after Layer 2
└── l3-domain.json        # Graph after Layer 3
```

**Purpose**:
- Debugging: Inspect what each layer contributed
- Resume: Start from any layer if needed
- Analysis: Compare layer outputs
- Validation: Verify incremental progress

### Indexes

Fast lookup structures for common queries:

```
enrichment/indexes/
└── entity-index.json    # Entity ID → metadata mapping
```

**Structure**:
```json
{
  "node-id": {
    "name": "User",
    "type": "class",
    "path": "models.py",
    "classification": "domain",
    "patterns": ["Entity"]
  }
}
```

## Extensibility Points

### 1. Adding New Layers

Create a new class extending `EnricherPass`:

```python
from enricher import EnricherPass

class Layer4Validator(EnricherPass):
    def __init__(self):
        super().__init__(layer_num=4, name="validator")

    def enrich_node(self, node, graph, context):
        # Access previous layers
        layer3 = node.get('enrichment', {}).get('layer3', {})

        # Your custom logic
        return {
            "confidence_score": 0.95,
            "validated": True
        }

    def enrich_edge(self, edge, graph, context):
        return {}
```

Register it:

```python
enricher.add_enricher(Layer4Validator())
```

### 2. Custom Classification Rules

Override methods in existing layers:

```python
from enricher.layer1_structural import StructuralEnricher

class CustomStructuralEnricher(StructuralEnricher):
    def _classify_by_name(self, name, node_type):
        # Add custom rules
        if 'widget' in name.lower():
            return 'domain'
        return super()._classify_by_name(name, node_type)
```

### 3. Custom Indexes

Add index generation in `IterativeEnricher._save_indexes()`:

```python
def _save_indexes(self, graph):
    # ... existing indexes ...

    # Custom workflow index
    workflow_index = {}
    for node in graph['nodes']:
        workflows = node.get('enrichment', {}) \
                        .get('layer3', {}) \
                        .get('workflow_participation', [])
        for workflow in workflows:
            if workflow not in workflow_index:
                workflow_index[workflow] = []
            workflow_index[workflow].append(node['id'])

    with open(self.enrichment_dir / 'indexes' / 'workflow-index.json', 'w') as f:
        json.dump(workflow_index, f, indent=2)
```

## Performance Considerations

### Memory

- Each iteration creates a deep copy of the graph
- Context stores all previous iterations
- For large graphs (>10K nodes), consider:
  - Streaming enrichment
  - Incremental updates
  - Context windowing (keep only N recent iterations)

### Speed

- Current implementation: O(n * layers * iterations) where n = nodes
- Bottlenecks:
  - File I/O for reading source code (Layer 1)
  - JSON serialization for saving artifacts
- Optimizations:
  - Cache file reads
  - Parallel node processing
  - Skip unchanged nodes in subsequent iterations

### Storage

Intermediate artifacts can be large:
- Each layer file ≈ size of enriched graph
- Example: 10K nodes ≈ 50MB per layer
- For 3 layers, 2 iterations: ~300MB

Consider:
- Delta storage (only changes)
- Compression (gzip)
- Cleanup old iterations

## Testing Strategy

### Unit Tests

Each enricher layer should have unit tests:

```python
def test_structural_classification():
    enricher = StructuralEnricher(Path('.'))
    node = {"name": "UserService", "type": "class"}
    result = enricher._classify_by_name("UserService", "class")
    assert result == "domain"
```

### Integration Tests

Test full pipeline:

```python
def test_full_enrichment():
    graph = load_test_graph()
    enricher = IterativeEnricher(graph, tmp_path)
    enricher.add_enricher(StructuralEnricher(test_data_path))
    enricher.add_enricher(SemanticEnricher())
    enricher.add_enricher(DomainEnricher())

    result = enricher.enrich(max_iterations=2)

    assert len(result['nodes']) == len(graph['nodes'])
    assert all('enrichment' in node for node in result['nodes'])
```

### Regression Tests

Keep example outputs and verify enrichment doesn't degrade:

```python
def test_example_unchanged():
    result = run_enricher('examples/test-code-data')
    expected = load_json('examples/test-code-data/expected-output.json')
    assert_graphs_equivalent(result, expected)
```

## Future Architecture Considerations

### Parallel Processing

For large codebases, nodes could be enriched in parallel:

```python
from multiprocessing import Pool

def enrich_nodes_parallel(self, nodes, enricher):
    with Pool() as pool:
        results = pool.starmap(
            enricher.enrich_node,
            [(node, self.graph, self.context) for node in nodes]
        )
    return results
```

### Incremental Updates

Track which nodes changed and only re-enrich affected subgraphs:

```python
def incremental_enrich(self, changed_node_ids):
    # Find affected nodes (neighbors, dependents)
    affected = self.find_affected_nodes(changed_node_ids)

    # Only enrich affected nodes
    for node in affected:
        self.enrich_node(node)
```

### Plugin System

Allow third-party enrichers:

```python
# Load enrichers from plugins
import importlib

for plugin_name in config['plugins']:
    module = importlib.import_module(f'enricher_plugins.{plugin_name}')
    enricher.add_enricher(module.create_enricher())
```

### ML Integration

Future layers could use machine learning:

```python
class MLSemanticEnricher(EnricherPass):
    def __init__(self, model_path):
        super().__init__(4, "ml-semantic")
        self.model = load_model(model_path)

    def enrich_node(self, node, graph, context):
        # Use trained model for classification
        features = extract_features(node, graph)
        prediction = self.model.predict(features)
        return {"ml_classification": prediction}
```
