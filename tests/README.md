# Test Suite

Comprehensive test suite for the Code Graph Enricher project.

## Overview

- **Total Tests**: 116
- **Test Coverage**: All major components (IterativeEnricher, Layer 1-3, CLI)
- **Test Framework**: pytest 8.4+

## Test Files

### `conftest.py`
Shared pytest fixtures and configuration:
- `sample_graph` - Basic test graph with various node types
- `entity_graph` - Graph for domain entity testing
- `temp_output_dir` - Temporary output directory
- `temp_source_dir` - Temporary source code directory with sample files
- `enriched_graph_layer1` - Pre-enriched with Layer 1 data
- `enriched_graph_layer2` - Pre-enriched with Layers 1 & 2 data

### `test_iterative_enricher.py` (16 tests)
Tests for core enrichment infrastructure:
- `TestEnricherPass` - Base class functionality (5 tests)
  - Initialization, node/edge processing, deep copying, multiple layers
- `TestIterativeEnricher` - Orchestrator functionality (11 tests)
  - Pipeline management, convergence detection, layer saving, statistics

### `test_layer1_structural.py` (19 tests)
Tests for structural enrichment layer:
- Node classification (infrastructure, domain, unknown)
- Complexity calculation (LOC, methods, nesting)
- Dependency analysis (imports, depth)
- Classification precedence (import vs name-based)

### `test_layer2_semantic.py` (42 tests)
Tests for semantic enrichment layer:
- Pattern detection (Entity, Service, Repository, Factory, DTO, ValueObject)
- Naming analysis (snake_case, camelCase, PascalCase)
- Method role classification (getter, setter, validator, calculator, etc.)
- API surface determination (public, private, protected)
- Edge semantic typing

### `test_layer3_domain.py` (22 tests)
Tests for domain enrichment layer:
- Domain concept extraction
- Business rule identification (validation, calculation, constraints)
- Workflow detection (auth, checkout, payment, etc.)
- Entity relationship inference (HAS_MANY, HAS_ONE, USES)
- Domain relationship classification

### `test_cli.py` (17 tests)
Tests for CLI functionality:
- Graph loading and validation
- Statistics printing
- Command-line argument parsing
- End-to-end enrichment execution
- Output file generation

## Running Tests

```bash
# Run all tests
./venv/bin/pytest tests/ -v

# Run specific test file
./venv/bin/pytest tests/test_layer1_structural.py -v

# Run specific test class
./venv/bin/pytest tests/test_layer1_structural.py::TestStructuralEnricher -v

# Run specific test method
./venv/bin/pytest tests/test_layer1_structural.py::TestStructuralEnricher::test_classify_by_name_domain -v

# Run tests matching a pattern
./venv/bin/pytest tests/ -k "classify" -v

# Run with coverage
./venv/bin/pytest tests/ --cov=enricher --cov-report=term-missing

# Generate HTML coverage report
./venv/bin/pytest tests/ --cov=enricher --cov-report=html
# Then open htmlcov/index.html
```

## Test Design Principles

1. **Isolation**: Each test is independent and can run in any order
2. **Clarity**: Test names clearly describe what is being tested
3. **Documentation**: Docstrings explain the purpose of each test
4. **Fixtures**: Reusable test data defined in conftest.py
5. **Coverage**: Tests cover both success and failure cases

## Adding New Tests

When adding new functionality:

1. Choose the appropriate test file based on the component
2. Add test methods to the relevant test class
3. Use descriptive names following the pattern `test_<what>_<scenario>`
4. Include a docstring explaining what the test verifies
5. Use existing fixtures where possible
6. Test edge cases and error conditions

Example:
```python
def test_classify_by_name_infrastructure(self, temp_source_dir):
    """Test classification of infrastructure nodes by name"""
    enricher = StructuralEnricher(temp_source_dir)

    # Infrastructure patterns
    assert enricher._classify_by_name("config.py", "file") == "infrastructure"
    assert enricher._classify_by_name("utils.py", "file") == "infrastructure"
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- No external dependencies required
- Uses temporary directories for all file operations
- Fast execution (< 1 second for full suite)
- Clear pass/fail reporting

## Troubleshooting

**ImportError: No module named 'enricher'**
- Solution: Install the package in editable mode: `./venv/bin/pip install -e .`

**Tests pass locally but fail in CI**
- Check that virtual environment is properly set up
- Ensure all dev dependencies are installed: `./venv/bin/pip install -e ".[dev]"`

**Fixture not found error**
- Make sure `conftest.py` is in the tests/ directory
- Check that pytest is discovering the tests/ directory

## Test Statistics

- Total: 116 tests
- IterativeEnricher: 16 tests (14%)
- Layer 1 (Structural): 19 tests (16%)
- Layer 2 (Semantic): 42 tests (36%)
- Layer 3 (Domain): 22 tests (19%)
- CLI: 17 tests (15%)
