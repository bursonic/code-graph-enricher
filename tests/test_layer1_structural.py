#!/usr/bin/env python3
"""
Tests for Layer 1: Structural Enrichment
"""

import pytest
from pathlib import Path
from enricher.layer1_structural import StructuralEnricher


class TestStructuralEnricher:
    """Test the StructuralEnricher class"""

    def test_initialization(self, temp_source_dir):
        """Test that StructuralEnricher initializes correctly"""
        enricher = StructuralEnricher(temp_source_dir)
        assert enricher.layer_num == 1
        assert enricher.name == "structural"
        assert enricher.root_path == temp_source_dir

    def test_classify_by_name_infrastructure(self, temp_source_dir):
        """Test classification of infrastructure nodes by name"""
        enricher = StructuralEnricher(temp_source_dir)

        # Infrastructure patterns
        assert enricher._classify_by_name("config.py", "file") == "infrastructure"
        assert enricher._classify_by_name("utils.py", "file") == "infrastructure"
        assert enricher._classify_by_name("BaseClass", "class") == "infrastructure"
        assert enricher._classify_by_name("test_helper", "function") == "infrastructure"
        assert enricher._classify_by_name("setup_logging", "function") == "infrastructure"

    def test_classify_by_name_domain(self, temp_source_dir):
        """Test classification of domain nodes by name"""
        enricher = StructuralEnricher(temp_source_dir)

        # Domain patterns
        assert enricher._classify_by_name("UserModel", "class") == "domain"
        assert enricher._classify_by_name("ProductService", "class") == "domain"
        assert enricher._classify_by_name("OrderRepository", "class") == "domain"
        assert enricher._classify_by_name("customer_entity", "class") == "domain"

    def test_classify_by_name_default_heuristics(self, temp_source_dir):
        """Test default classification heuristics"""
        enricher = StructuralEnricher(temp_source_dir)

        # Files default to infrastructure
        assert enricher._classify_by_name("something.py", "file") == "infrastructure"

        # Classes default to domain
        assert enricher._classify_by_name("SomeClass", "class") == "domain"

        # Functions without clear indicators
        assert enricher._classify_by_name("process_data", "function") == "unknown"

    def test_classify_by_imports_stdlib(self, temp_source_dir):
        """Test classification based on standard library imports"""
        enricher = StructuralEnricher(temp_source_dir)

        node = {
            "type": "file",
            "metadata": {
                "imports": ["os", "sys", "json", "logging"]
            }
        }

        classification = enricher._classify_by_imports(node, {})
        assert classification == "infrastructure"

    def test_classify_by_imports_domain(self, temp_source_dir):
        """Test classification based on local/domain imports"""
        enricher = StructuralEnricher(temp_source_dir)

        node = {
            "type": "file",
            "metadata": {
                "imports": ["models", "services", "repositories", "json"]
            }
        }

        classification = enricher._classify_by_imports(node, {})
        assert classification in ["domain", "mixed"]

    def test_classify_by_imports_non_file(self, temp_source_dir):
        """Test that classify_by_imports returns None for non-file nodes"""
        enricher = StructuralEnricher(temp_source_dir)

        node = {
            "type": "class",
            "metadata": {}
        }

        classification = enricher._classify_by_imports(node, {})
        assert classification is None

    def test_calculate_complexity_file_with_source(self, temp_source_dir):
        """Test complexity calculation for a file with actual source code"""
        enricher = StructuralEnricher(temp_source_dir)

        node = {
            "id": "file1",
            "type": "file",
            "path": "src/services/user_service.py",
            "metadata": {}
        }

        graph = {"nodes": [node], "edges": []}
        complexity = enricher._calculate_complexity(node, graph)

        assert 'loc' in complexity
        assert complexity['loc'] > 0  # Should have counted lines
        assert complexity['nesting_depth'] == 0
        assert complexity['num_params'] == 0
        assert complexity['num_methods'] == 0

    def test_calculate_complexity_class(self, temp_source_dir):
        """Test complexity calculation for a class"""
        enricher = StructuralEnricher(temp_source_dir)

        node = {
            "id": "class1",
            "type": "class",
            "path": "src/services/user_service.py",
            "metadata": {}
        }

        # Create graph with contained methods
        graph = {
            "nodes": [node],
            "edges": [
                {"source": "class1", "target": "method1", "type": "contains"},
                {"source": "class1", "target": "method2", "type": "contains"},
                {"source": "class1", "target": "method3", "type": "contains"}
            ]
        }

        complexity = enricher._calculate_complexity(node, graph)

        assert complexity['num_methods'] == 3
        assert complexity['loc'] > 0  # Estimated based on methods

    def test_calculate_complexity_function(self, temp_source_dir):
        """Test complexity calculation for a function"""
        enricher = StructuralEnricher(temp_source_dir)

        node = {
            "id": "func1",
            "type": "function",
            "path": "src/services/user_service.py",
            "metadata": {}
        }

        graph = {"nodes": [node], "edges": []}
        complexity = enricher._calculate_complexity(node, graph)

        assert complexity['loc'] >= 0
        assert complexity['nesting_depth'] >= 0

    def test_calculate_complexity_missing_file(self, temp_source_dir):
        """Test complexity calculation when source file doesn't exist"""
        enricher = StructuralEnricher(temp_source_dir)

        node = {
            "id": "file1",
            "type": "file",
            "path": "nonexistent/file.py",
            "metadata": {}
        }

        graph = {"nodes": [node], "edges": []}
        complexity = enricher._calculate_complexity(node, graph)

        # Should return default values without crashing
        assert complexity['loc'] == 0
        assert complexity['nesting_depth'] == 0

    def test_calculate_dependencies_file(self, temp_source_dir):
        """Test dependency calculation for a file"""
        enricher = StructuralEnricher(temp_source_dir)

        node = {
            "type": "file",
            "metadata": {
                "imports": ["os", "json", "models", "services"]
            }
        }

        graph = {"nodes": [node], "edges": []}
        deps = enricher._calculate_dependencies(node, graph)

        assert deps['num_imports'] == 4
        assert deps['imports_from'] == ["os", "json", "models", "services"]
        assert deps['import_depth'] in [0, 1]

    def test_calculate_dependencies_stdlib_only(self, temp_source_dir):
        """Test dependency calculation with only stdlib imports"""
        enricher = StructuralEnricher(temp_source_dir)

        node = {
            "type": "file",
            "metadata": {
                "imports": ["os", "sys", "json"]
            }
        }

        graph = {"nodes": [node], "edges": []}
        deps = enricher._calculate_dependencies(node, graph)

        assert deps['num_imports'] == 3
        assert deps['import_depth'] == 0  # Only stdlib

    def test_calculate_dependencies_local_imports(self, temp_source_dir):
        """Test dependency calculation with local imports"""
        enricher = StructuralEnricher(temp_source_dir)

        node = {
            "type": "file",
            "metadata": {
                "imports": ["models", "services", "repositories"]
            }
        }

        graph = {"nodes": [node], "edges": []}
        deps = enricher._calculate_dependencies(node, graph)

        assert deps['num_imports'] == 3
        assert deps['import_depth'] == 1  # Has local imports

    def test_enrich_node_full(self, sample_graph, temp_source_dir):
        """Test full node enrichment"""
        enricher = StructuralEnricher(temp_source_dir)

        node = sample_graph['nodes'][0]  # File node
        result = enricher.enrich_node(node, sample_graph, context=[])

        # Check all enrichment fields are present
        assert 'classification' in result
        assert 'complexity' in result
        assert 'dependencies' in result

        # Check complexity structure
        assert 'loc' in result['complexity']
        assert 'nesting_depth' in result['complexity']
        assert 'num_params' in result['complexity']
        assert 'num_methods' in result['complexity']

        # Check dependencies structure
        assert 'import_depth' in result['dependencies']
        assert 'num_imports' in result['dependencies']
        assert 'imports_from' in result['dependencies']

    def test_enrich_node_classification_precedence(self, temp_source_dir):
        """Test that import-based classification takes precedence over name-based"""
        enricher = StructuralEnricher(temp_source_dir)

        # Node with conflicting signals: name suggests domain, imports suggest infra
        node = {
            "id": "file1",
            "type": "file",
            "name": "user_service.py",  # Domain name
            "path": "user_service.py",
            "location": {"line": 1, "column": 0},
            "metadata": {
                "imports": ["os", "sys", "json"]  # Infrastructure imports
            }
        }

        graph = {"nodes": [node], "edges": []}
        result = enricher.enrich_node(node, graph, context=[])

        # Import classification should take precedence
        assert result['classification'] == "infrastructure"

    def test_enrich_edge(self, sample_graph, temp_source_dir):
        """Test edge enrichment"""
        enricher = StructuralEnricher(temp_source_dir)

        edge = sample_graph['edges'][0]
        result = enricher.enrich_edge(edge, sample_graph, context=[])

        assert 'weight' in result
        assert 'depth' in result
        assert result['weight'] == 1.0
        assert result['depth'] == 1

    def test_process_full_graph(self, sample_graph, temp_source_dir):
        """Test processing an entire graph"""
        enricher = StructuralEnricher(temp_source_dir)
        result = enricher.process(sample_graph, context=[])

        # All nodes should have layer1 enrichment
        for node in result['nodes']:
            assert 'enrichment' in node
            assert 'layer1' in node['enrichment']
            assert 'classification' in node['enrichment']['layer1']
            assert 'complexity' in node['enrichment']['layer1']
            assert 'dependencies' in node['enrichment']['layer1']

        # All edges should have layer1 enrichment
        for edge in result['edges']:
            assert 'enrichment' in edge
            assert 'layer1' in edge['enrichment']
            assert 'weight' in edge['enrichment']['layer1']
            assert 'depth' in edge['enrichment']['layer1']

    def test_enrich_node_with_context(self, sample_graph, temp_source_dir):
        """Test that enricher can receive context from previous iterations"""
        enricher = StructuralEnricher(temp_source_dir)

        # First iteration
        node = sample_graph['nodes'][0]
        result1 = enricher.enrich_node(node, sample_graph, context=[])

        # Second iteration with context
        context = [sample_graph]
        result2 = enricher.enrich_node(node, sample_graph, context=context)

        # Both should produce results (context is available but may not change results)
        assert 'classification' in result1
        assert 'classification' in result2
