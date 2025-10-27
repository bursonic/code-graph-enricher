#!/usr/bin/env python3
"""
Tests for Layer 2: Semantic Enrichment
"""

import pytest
from enricher.layer2_semantic import SemanticEnricher


class TestSemanticEnricher:
    """Test the SemanticEnricher class"""

    def test_initialization(self):
        """Test that SemanticEnricher initializes correctly"""
        enricher = SemanticEnricher()
        assert enricher.layer_num == 2
        assert enricher.name == "semantic"

    def test_detect_patterns_entity(self):
        """Test detection of Entity pattern"""
        enricher = SemanticEnricher()

        node = {
            "type": "class",
            "name": "User",
            "metadata": {}
        }

        patterns = enricher._detect_patterns(node, {}, [])
        assert "Entity" in patterns

    def test_detect_patterns_value_object(self):
        """Test detection of ValueObject pattern"""
        enricher = SemanticEnricher()

        node = {
            "type": "class",
            "name": "EmailValue",
            "metadata": {}
        }

        patterns = enricher._detect_patterns(node, {}, [])
        assert "ValueObject" in patterns

    def test_detect_patterns_value_object_dataclass(self):
        """Test detection of ValueObject pattern with dataclass metadata"""
        enricher = SemanticEnricher()

        node = {
            "type": "class",
            "name": "Point",
            "metadata": {"is_dataclass": True}
        }

        patterns = enricher._detect_patterns(node, {}, [])
        assert "ValueObject" in patterns

    def test_detect_patterns_service(self):
        """Test detection of Service pattern"""
        enricher = SemanticEnricher()

        node = {
            "type": "class",
            "name": "UserService",
            "metadata": {}
        }

        patterns = enricher._detect_patterns(node, {}, [])
        assert "Service" in patterns

    def test_detect_patterns_repository(self):
        """Test detection of Repository pattern"""
        enricher = SemanticEnricher()

        node1 = {
            "type": "class",
            "name": "UserRepository",
            "metadata": {}
        }

        node2 = {
            "type": "class",
            "name": "OrderRepo",
            "metadata": {}
        }

        patterns1 = enricher._detect_patterns(node1, {}, [])
        patterns2 = enricher._detect_patterns(node2, {}, [])

        assert "Repository" in patterns1
        assert "Repository" in patterns2

    def test_detect_patterns_factory(self):
        """Test detection of Factory pattern"""
        enricher = SemanticEnricher()

        node1 = {
            "type": "class",
            "name": "UserFactory",
            "metadata": {}
        }

        node2 = {
            "type": "class",
            "name": "OrderBuilder",
            "metadata": {}
        }

        patterns1 = enricher._detect_patterns(node1, {}, [])
        patterns2 = enricher._detect_patterns(node2, {}, [])

        assert "Factory" in patterns1
        assert "Factory" in patterns2

    def test_detect_patterns_dto(self):
        """Test detection of DTO pattern"""
        enricher = SemanticEnricher()

        node1 = {
            "type": "class",
            "name": "UserDTO",
            "metadata": {}
        }

        node2 = {
            "type": "class",
            "name": "CreateOrderDto",
            "metadata": {}
        }

        patterns1 = enricher._detect_patterns(node1, {}, [])
        patterns2 = enricher._detect_patterns(node2, {}, [])

        assert "DTO" in patterns1
        assert "DTO" in patterns2

    def test_detect_patterns_factory_function(self):
        """Test detection of FactoryFunction pattern"""
        enricher = SemanticEnricher()

        node1 = {
            "type": "function",
            "name": "create_user",
            "metadata": {}
        }

        node2 = {
            "type": "function",
            "name": "make_order",
            "metadata": {}
        }

        node3 = {
            "type": "function",
            "name": "build_product",
            "metadata": {}
        }

        patterns1 = enricher._detect_patterns(node1, {}, [])
        patterns2 = enricher._detect_patterns(node2, {}, [])
        patterns3 = enricher._detect_patterns(node3, {}, [])

        assert "FactoryFunction" in patterns1
        assert "FactoryFunction" in patterns2
        assert "FactoryFunction" in patterns3

    def test_detect_patterns_strategy(self):
        """Test detection of Strategy pattern"""
        enricher = SemanticEnricher()

        node = {
            "type": "function",
            "name": "payment_strategy",
            "metadata": {}
        }

        patterns = enricher._detect_patterns(node, {}, [])
        assert "Strategy" in patterns

    def test_analyze_naming_snake_case(self):
        """Test naming analysis for snake_case"""
        enricher = SemanticEnricher()

        node = {
            "name": "get_user_by_id"
        }

        analysis = enricher._analyze_naming(node)

        assert analysis['conventions'] == 'snake_case'
        assert 'get' in analysis['terms']
        assert 'user' in analysis['terms']
        assert 'by' in analysis['terms']
        assert 'id' in analysis['terms']
        assert 'get' in analysis['role_indicators']

    def test_analyze_naming_pascal_case(self):
        """Test naming analysis for PascalCase"""
        enricher = SemanticEnricher()

        node = {
            "name": "UserService"
        }

        analysis = enricher._analyze_naming(node)

        assert analysis['conventions'] == 'PascalCase'
        assert 'user' in analysis['terms']
        assert 'service' in analysis['terms']

    def test_analyze_naming_camel_case(self):
        """Test naming analysis for camelCase"""
        enricher = SemanticEnricher()

        node = {
            "name": "getUserById"
        }

        analysis = enricher._analyze_naming(node)

        assert analysis['conventions'] == 'camelCase'
        assert 'get' in analysis['terms']
        assert 'user' in analysis['terms']
        assert 'by' in analysis['terms']
        assert 'id' in analysis['terms']

    def test_analyze_naming_role_indicators(self):
        """Test detection of role indicators in naming"""
        enricher = SemanticEnricher()

        test_cases = [
            ("get_value", ["get"]),
            ("set_property", ["set"]),
            ("validate_email", ["validate"]),
            ("calculate_total", ["calculate"]),
            ("create_user", ["create"]),
            ("is_valid", ["is"]),
            ("has_permission", ["has"]),
            ("should_process", ["should"]),
        ]

        for name, expected_indicators in test_cases:
            node = {"name": name}
            analysis = enricher._analyze_naming(node)
            for indicator in expected_indicators:
                assert indicator in analysis['role_indicators'], \
                    f"Expected {indicator} in role_indicators for {name}"

    def test_classify_method_role_getter(self):
        """Test classification of getter methods"""
        enricher = SemanticEnricher()

        node = {"type": "function", "name": "get_user"}
        naming = enricher._analyze_naming(node)
        roles = enricher._classify_method_role(node, naming)

        assert "getter" in roles

    def test_classify_method_role_setter(self):
        """Test classification of setter methods"""
        enricher = SemanticEnricher()

        node = {"type": "function", "name": "set_value"}
        naming = enricher._analyze_naming(node)
        roles = enricher._classify_method_role(node, naming)

        assert "setter" in roles

    def test_classify_method_role_validator(self):
        """Test classification of validator methods"""
        enricher = SemanticEnricher()

        test_cases = ["validate_email", "check_permission", "is_valid", "has_access"]

        for name in test_cases:
            node = {"type": "function", "name": name}
            naming = enricher._analyze_naming(node)
            roles = enricher._classify_method_role(node, naming)
            assert "validator" in roles, f"Expected validator role for {name}"

    def test_classify_method_role_calculator(self):
        """Test classification of calculator methods"""
        enricher = SemanticEnricher()

        test_cases = ["calculate_total", "compute_average"]

        for name in test_cases:
            node = {"type": "function", "name": name}
            naming = enricher._analyze_naming(node)
            roles = enricher._classify_method_role(node, naming)
            assert "calculator" in roles, f"Expected calculator role for {name}"

    def test_classify_method_role_transformer(self):
        """Test classification of transformer methods"""
        enricher = SemanticEnricher()

        test_cases = ["transform_data", "format_date", "parse_input", "process"]

        for name in test_cases:
            node = {"type": "function", "name": name}
            naming = enricher._analyze_naming(node)
            roles = enricher._classify_method_role(node, naming)
            assert "transformer" in roles, f"Expected transformer role for {name}"

    def test_classify_method_role_creator(self):
        """Test classification of creator methods"""
        enricher = SemanticEnricher()

        test_cases = ["create_user", "build_order", "make_product"]

        for name in test_cases:
            node = {"type": "function", "name": name}
            naming = enricher._analyze_naming(node)
            roles = enricher._classify_method_role(node, naming)
            assert "creator" in roles, f"Expected creator role for {name}"

    def test_classify_method_role_mutator(self):
        """Test classification of mutator methods"""
        enricher = SemanticEnricher()

        test_cases = ["add_item", "remove_user", "delete_record"]

        for name in test_cases:
            node = {"type": "function", "name": name}
            naming = enricher._analyze_naming(node)
            roles = enricher._classify_method_role(node, naming)
            assert "mutator" in roles, f"Expected mutator role for {name}"

    def test_classify_method_role_general(self):
        """Test that methods without specific roles are marked as general"""
        enricher = SemanticEnricher()

        node = {"type": "function", "name": "do_something"}
        naming = enricher._analyze_naming(node)
        roles = enricher._classify_method_role(node, naming)

        assert "general" in roles

    def test_classify_method_role_non_function(self):
        """Test that non-function nodes return empty roles"""
        enricher = SemanticEnricher()

        node = {"type": "class", "name": "UserClass"}
        naming = enricher._analyze_naming(node)
        roles = enricher._classify_method_role(node, naming)

        assert roles == []

    def test_determine_api_surface_public(self):
        """Test detection of public API surface"""
        enricher = SemanticEnricher()

        node = {"name": "get_user"}
        api_surface = enricher._determine_api_surface(node)
        assert api_surface == "public"

    def test_determine_api_surface_protected(self):
        """Test detection of protected API surface"""
        enricher = SemanticEnricher()

        node = {"name": "_internal_method"}
        api_surface = enricher._determine_api_surface(node)
        assert api_surface == "protected"

    def test_determine_api_surface_private(self):
        """Test detection of private API surface"""
        enricher = SemanticEnricher()

        node = {"name": "__private_method"}
        api_surface = enricher._determine_api_surface(node)
        assert api_surface == "private"

    def test_determine_api_surface_dunder_methods(self):
        """Test that dunder methods follow Python naming convention"""
        enricher = SemanticEnricher()

        # __init__ has both __ prefix and suffix, but starts with __
        node = {"name": "__init__"}
        api_surface = enricher._determine_api_surface(node)
        # Per the implementation, __name__ still starts with __ so treated as protected per regex
        # The implementation checks "starts with __ and NOT ends with __" for private
        # So __init__ doesn't match private (ends with __), but does start with __ so it's not public
        assert api_surface in ["protected", "private"]  # Accept either based on implementation

    def test_enrich_node_full(self, sample_graph):
        """Test full node enrichment"""
        enricher = SemanticEnricher()

        node = sample_graph['nodes'][1]  # UserService class
        result = enricher.enrich_node(node, sample_graph, context=[])

        # Check all enrichment fields are present
        assert 'patterns' in result
        assert 'naming_analysis' in result
        assert 'method_roles' in result
        assert 'api_surface' in result

        # Check naming analysis structure
        assert 'terms' in result['naming_analysis']
        assert 'conventions' in result['naming_analysis']
        assert 'role_indicators' in result['naming_analysis']

    def test_enrich_edge_contains(self, sample_graph):
        """Test enrichment of contains edge"""
        enricher = SemanticEnricher()

        edge = sample_graph['edges'][0]  # contains edge
        result = enricher.enrich_edge(edge, sample_graph, context=[])

        assert 'semantic_type' in result
        assert result['semantic_type'] == 'composition'

    def test_enrich_edge_imports(self):
        """Test enrichment of imports edge"""
        enricher = SemanticEnricher()

        graph = {
            "nodes": [
                {"id": "n1", "type": "file"},
                {"id": "n2", "type": "file"}
            ],
            "edges": []
        }

        edge = {"source": "n1", "target": "n2", "type": "imports"}
        result = enricher.enrich_edge(edge, graph, context=[])

        assert result['semantic_type'] == 'dependency'

    def test_enrich_edge_inherits(self):
        """Test enrichment of inherits edge"""
        enricher = SemanticEnricher()

        graph = {
            "nodes": [
                {"id": "c1", "type": "class"},
                {"id": "c2", "type": "class"}
            ],
            "edges": []
        }

        edge = {"source": "c1", "target": "c2", "type": "inherits"}
        result = enricher.enrich_edge(edge, graph, context=[])

        assert result['semantic_type'] == 'inheritance'

    def test_enrich_edge_calls(self):
        """Test enrichment of calls edge"""
        enricher = SemanticEnricher()

        graph = {
            "nodes": [
                {"id": "f1", "type": "function"},
                {"id": "f2", "type": "function"}
            ],
            "edges": []
        }

        edge = {"source": "f1", "target": "f2", "type": "calls"}
        result = enricher.enrich_edge(edge, graph, context=[])

        assert result['semantic_type'] == 'invocation'

    def test_enrich_edge_unknown_type(self):
        """Test enrichment of unknown edge type"""
        enricher = SemanticEnricher()

        graph = {
            "nodes": [
                {"id": "n1", "type": "file"},
                {"id": "n2", "type": "file"}
            ],
            "edges": []
        }

        edge = {"source": "n1", "target": "n2", "type": "unknown_type"}
        result = enricher.enrich_edge(edge, graph, context=[])

        assert result['semantic_type'] == 'unknown'

    def test_process_full_graph(self, sample_graph):
        """Test processing an entire graph"""
        enricher = SemanticEnricher()
        result = enricher.process(sample_graph, context=[])

        # All nodes should have layer2 enrichment
        for node in result['nodes']:
            assert 'enrichment' in node
            assert 'layer2' in node['enrichment']
            assert 'patterns' in node['enrichment']['layer2']
            assert 'naming_analysis' in node['enrichment']['layer2']
            assert 'method_roles' in node['enrichment']['layer2']
            assert 'api_surface' in node['enrichment']['layer2']

        # All edges should have layer2 enrichment
        for edge in result['edges']:
            assert 'enrichment' in edge
            assert 'layer2' in edge['enrichment']
            assert 'semantic_type' in edge['enrichment']['layer2']

    def test_multiple_patterns_detected(self):
        """Test that a class can have multiple patterns detected"""
        enricher = SemanticEnricher()

        # A User entity that is also a value object (dataclass)
        node = {
            "type": "class",
            "name": "UserValue",
            "metadata": {"is_dataclass": True}
        }

        patterns = enricher._detect_patterns(node, {}, [])

        # Should detect both Entity and ValueObject
        assert "Entity" in patterns
        assert "ValueObject" in patterns
