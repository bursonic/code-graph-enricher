#!/usr/bin/env python3
"""
Tests for Layer 3: Domain Enrichment
"""

import pytest
from enricher.layer3_domain import DomainEnricher


class TestDomainEnricher:
    """Test the DomainEnricher class"""

    def test_initialization(self):
        """Test that DomainEnricher initializes correctly"""
        enricher = DomainEnricher()
        assert enricher.layer_num == 3
        assert enricher.name == "domain"

    def test_extract_domain_concepts_from_entity(self, enriched_graph_layer2):
        """Test domain concept extraction from Entity nodes"""
        enricher = DomainEnricher()

        # Find a class node and add Entity pattern to it
        class_node = next(n for n in enriched_graph_layer2['nodes'] if n['type'] == 'class')
        class_node['enrichment']['layer2']['patterns'] = ['Entity']

        concepts = enricher._extract_domain_concepts(class_node, enriched_graph_layer2, [])

        assert class_node['name'] in concepts

    def test_extract_domain_concepts_from_value_object(self, enriched_graph_layer2):
        """Test domain concept extraction from ValueObject nodes"""
        enricher = DomainEnricher()

        class_node = next(n for n in enriched_graph_layer2['nodes'] if n['type'] == 'class')
        class_node['enrichment']['layer2']['patterns'] = ['ValueObject']

        concepts = enricher._extract_domain_concepts(class_node, enriched_graph_layer2, [])

        assert class_node['name'] in concepts

    def test_extract_domain_concepts_from_naming(self):
        """Test domain concept extraction from naming terms"""
        enricher = DomainEnricher()

        node = {
            "type": "function",
            "name": "process_user_order",
            "enrichment": {
                "layer2": {
                    "patterns": [],
                    "naming_analysis": {
                        "terms": ["process", "user", "order"]
                    }
                }
            }
        }

        concepts = enricher._extract_domain_concepts(node, {}, [])

        assert "User" in concepts
        assert "Order" in concepts

    def test_extract_domain_concepts_deduplication(self):
        """Test that duplicate domain concepts are removed"""
        enricher = DomainEnricher()

        node = {
            "type": "class",
            "name": "User",
            "enrichment": {
                "layer2": {
                    "patterns": ["Entity"],
                    "naming_analysis": {
                        "terms": ["user"]  # Same as class name
                    }
                }
            }
        }

        concepts = enricher._extract_domain_concepts(node, {}, [])

        # Should only have "User" once despite appearing in both name and terms
        assert concepts.count("User") == 1

    def test_identify_business_rules_validator(self):
        """Test identification of validation business rules"""
        enricher = DomainEnricher()

        node = {
            "type": "function",
            "name": "validate_email",
            "path": "validators.py",
            "location": {"line": 10},
            "enrichment": {
                "layer2": {
                    "method_roles": ["validator"],
                    "naming_analysis": {}
                }
            }
        }

        rules = enricher._identify_business_rules(node, {}, [])

        assert len(rules) > 0
        assert any(r['type'] == 'validation' for r in rules)

    def test_identify_business_rules_calculator(self):
        """Test identification of calculation business rules"""
        enricher = DomainEnricher()

        node = {
            "type": "function",
            "name": "calculate_total",
            "path": "calculations.py",
            "location": {"line": 20},
            "enrichment": {
                "layer2": {
                    "method_roles": ["calculator"],
                    "naming_analysis": {}
                }
            }
        }

        rules = enricher._identify_business_rules(node, {}, [])

        assert len(rules) > 0
        assert any(r['type'] == 'calculation' for r in rules)

    def test_identify_business_rules_constraint(self):
        """Test identification of constraint business rules"""
        enricher = DomainEnricher()

        test_names = ["apply_discount", "check_permission", "verify_age", "enforce_limit"]

        for name in test_names:
            node = {
                "type": "function",
                "name": name,
                "path": "rules.py",
                "location": {"line": 30},
                "enrichment": {
                    "layer2": {
                        "method_roles": [],
                        "naming_analysis": {}
                    }
                }
            }

            rules = enricher._identify_business_rules(node, {}, [])

            assert len(rules) > 0, f"Expected business rule for {name}"
            assert any(r['type'] == 'constraint' for r in rules), \
                f"Expected constraint rule for {name}"

    def test_identify_business_rules_non_function(self):
        """Test that non-function nodes don't generate business rules"""
        enricher = DomainEnricher()

        node = {
            "type": "class",
            "name": "UserClass"
        }

        rules = enricher._identify_business_rules(node, {}, [])
        assert rules == []

    def test_detect_workflow_participation_authentication(self):
        """Test detection of authentication workflow"""
        enricher = DomainEnricher()

        test_cases = ["login", "logout", "authenticate_user", "verify_token"]

        for name in test_cases:
            node = {"type": "function", "name": name}
            workflows = enricher._detect_workflow_participation(node, {}, [])
            assert "authentication" in workflows, f"Expected authentication workflow for {name}"

    def test_detect_workflow_participation_registration(self):
        """Test detection of registration workflow"""
        enricher = DomainEnricher()

        test_cases = ["register", "signup", "create_account"]

        for name in test_cases:
            node = {"type": "function", "name": name}
            workflows = enricher._detect_workflow_participation(node, {}, [])
            assert "registration" in workflows, f"Expected registration workflow for {name}"

    def test_detect_workflow_participation_checkout(self):
        """Test detection of checkout workflow"""
        enricher = DomainEnricher()

        test_cases = ["checkout", "purchase", "buy_product", "place_order"]

        for name in test_cases:
            node = {"type": "function", "name": name}
            workflows = enricher._detect_workflow_participation(node, {}, [])
            assert "checkout" in workflows, f"Expected checkout workflow for {name}"

    def test_detect_workflow_participation_cart(self):
        """Test detection of cart management workflow"""
        enricher = DomainEnricher()

        test_cases = ["add_to_cart", "remove_from_cart", "update_cart", "clear_cart"]

        for name in test_cases:
            node = {"type": "function", "name": name}
            workflows = enricher._detect_workflow_participation(node, {}, [])
            assert "cart_management" in workflows, f"Expected cart_management workflow for {name}"

    def test_detect_workflow_participation_payment(self):
        """Test detection of payment workflow"""
        enricher = DomainEnricher()

        test_cases = ["pay", "charge_card", "process_payment", "refund_payment"]

        for name in test_cases:
            node = {"type": "function", "name": name}
            workflows = enricher._detect_workflow_participation(node, {}, [])
            assert "payment" in workflows, f"Expected payment workflow for {name}"

    def test_detect_workflow_participation_order_fulfillment(self):
        """Test detection of order fulfillment workflow"""
        enricher = DomainEnricher()

        test_cases = ["ship_order", "deliver_package", "fulfill_request", "track_shipment"]

        for name in test_cases:
            node = {"type": "function", "name": name}
            workflows = enricher._detect_workflow_participation(node, {}, [])
            assert "order_fulfillment" in workflows, \
                f"Expected order_fulfillment workflow for {name}"

    def test_detect_workflow_participation_non_function(self):
        """Test that non-function nodes don't participate in workflows"""
        enricher = DomainEnricher()

        node = {"type": "class", "name": "UserClass"}
        workflows = enricher._detect_workflow_participation(node, {}, [])
        assert workflows == []

    def test_infer_entity_relationships_has_many(self, entity_graph):
        """Test inference of HAS_MANY relationships"""
        enricher = DomainEnricher()

        # Add Entity pattern to User class
        user_class = next(n for n in entity_graph['nodes'] if n['id'] == 'class_user')
        user_class['enrichment'] = {
            'layer2': {'patterns': ['Entity']}
        }

        # Add get_orders function
        get_orders = next(n for n in entity_graph['nodes'] if n['id'] == 'func_get_orders')

        relationships = enricher._infer_entity_relationships(user_class, entity_graph, [])

        # Should infer User HAS_MANY Order
        has_many = [r for r in relationships if r['type'] == 'HAS_MANY']
        assert len(has_many) > 0
        assert any('order' in r['target'].lower() for r in has_many)

    def test_infer_entity_relationships_has_one(self):
        """Test inference of HAS_ONE relationships"""
        enricher = DomainEnricher()

        graph = {
            "nodes": [
                {
                    "id": "user_class",
                    "type": "class",
                    "name": "User",
                    "enrichment": {"layer2": {"patterns": ["Entity"]}}
                },
                {
                    "id": "get_profile",
                    "type": "function",
                    "name": "get_profile"
                }
            ],
            "edges": [
                {"source": "user_class", "target": "get_profile", "type": "contains"}
            ]
        }

        user_class = graph['nodes'][0]
        relationships = enricher._infer_entity_relationships(user_class, graph, [])

        # Should infer User HAS_ONE Profile
        has_one = [r for r in relationships if r['type'] == 'HAS_ONE']
        assert len(has_one) > 0
        assert any('profile' in r['target'].lower() for r in has_one)

    def test_infer_entity_relationships_uses(self):
        """Test inference of USES relationships"""
        enricher = DomainEnricher()

        graph = {
            "nodes": [
                {
                    "id": "order_class",
                    "type": "class",
                    "name": "Order",
                    "enrichment": {"layer2": {"patterns": ["Entity"]}}
                },
                {
                    "id": "add_discount",
                    "type": "function",
                    "name": "add_discount"
                },
                {
                    "id": "use_coupon",
                    "type": "function",
                    "name": "use_coupon"
                }
            ],
            "edges": [
                {"source": "order_class", "target": "add_discount", "type": "contains"},
                {"source": "order_class", "target": "use_coupon", "type": "contains"}
            ]
        }

        order_class = graph['nodes'][0]
        relationships = enricher._infer_entity_relationships(order_class, graph, [])

        # Should infer USES relationships
        uses = [r for r in relationships if r['type'] == 'USES']
        assert len(uses) > 0

    def test_infer_entity_relationships_non_entity(self):
        """Test that non-entity classes don't generate relationships"""
        enricher = DomainEnricher()

        graph = {
            "nodes": [
                {
                    "id": "service_class",
                    "type": "class",
                    "name": "UserService",
                    "enrichment": {"layer2": {"patterns": ["Service"]}}  # Not Entity
                }
            ],
            "edges": []
        }

        service_class = graph['nodes'][0]
        relationships = enricher._infer_entity_relationships(service_class, graph, [])

        assert relationships == []

    def test_infer_entity_relationships_non_class(self):
        """Test that non-class nodes don't generate relationships"""
        enricher = DomainEnricher()

        graph = {
            "nodes": [
                {
                    "id": "function",
                    "type": "function",
                    "name": "get_user",
                    "enrichment": {"layer2": {"patterns": []}}
                }
            ],
            "edges": []
        }

        func_node = graph['nodes'][0]
        relationships = enricher._infer_entity_relationships(func_node, graph, [])

        assert relationships == []

    def test_enrich_node_full(self, entity_graph):
        """Test full node enrichment"""
        enricher = DomainEnricher()

        # Add layer2 enrichment to node
        node = entity_graph['nodes'][0]
        node['enrichment'] = {
            'layer2': {
                'patterns': ['Entity'],
                'naming_analysis': {'terms': ['user']},
                'method_roles': []
            }
        }

        result = enricher.enrich_node(node, entity_graph, context=[])

        # Check all enrichment fields are present
        assert 'domain_concepts' in result
        assert 'business_rules' in result
        assert 'workflow_participation' in result
        assert 'entity_relationships' in result

    def test_enrich_edge_contains_entity(self):
        """Test edge enrichment for contains relationship with entity"""
        enricher = DomainEnricher()

        graph = {
            "nodes": [
                {
                    "id": "user_class",
                    "type": "class",
                    "name": "User",
                    "enrichment": {"layer2": {"patterns": ["Entity"]}}
                },
                {
                    "id": "method",
                    "type": "function",
                    "name": "get_name"
                }
            ],
            "edges": []
        }

        edge = {"source": "user_class", "target": "method", "type": "contains"}
        result = enricher.enrich_edge(edge, graph, context=[])

        assert 'domain_relationship' in result
        assert result['domain_relationship'] == 'DEFINES'

    def test_enrich_edge_imports_entities(self):
        """Test edge enrichment for imports between entities"""
        enricher = DomainEnricher()

        graph = {
            "nodes": [
                {
                    "id": "user",
                    "type": "class",
                    "name": "User",
                    "enrichment": {"layer2": {"patterns": ["Entity"]}}
                },
                {
                    "id": "order",
                    "type": "class",
                    "name": "Order",
                    "enrichment": {"layer2": {"patterns": ["Entity"]}}
                }
            ],
            "edges": []
        }

        edge = {"source": "user", "target": "order", "type": "imports"}
        result = enricher.enrich_edge(edge, graph, context=[])

        assert 'domain_relationship' in result
        assert result['domain_relationship'] == 'DEPENDS_ON'

    def test_enrich_edge_imports_service(self):
        """Test edge enrichment for imports from service"""
        enricher = DomainEnricher()

        graph = {
            "nodes": [
                {
                    "id": "service",
                    "type": "class",
                    "name": "UserService",
                    "enrichment": {"layer2": {"patterns": ["Service"]}}
                },
                {
                    "id": "repo",
                    "type": "class",
                    "name": "UserRepository",
                    "enrichment": {"layer2": {"patterns": ["Repository"]}}
                }
            ],
            "edges": []
        }

        edge = {"source": "service", "target": "repo", "type": "imports"}
        result = enricher.enrich_edge(edge, graph, context=[])

        assert 'domain_relationship' in result
        assert result['domain_relationship'] == 'USES'

    def test_enrich_edge_calls(self):
        """Test edge enrichment for calls relationship"""
        enricher = DomainEnricher()

        graph = {
            "nodes": [
                {"id": "f1", "type": "function", "enrichment": {"layer2": {"patterns": []}}},
                {"id": "f2", "type": "function", "enrichment": {"layer2": {"patterns": []}}}
            ],
            "edges": []
        }

        edge = {"source": "f1", "target": "f2", "type": "calls"}
        result = enricher.enrich_edge(edge, graph, context=[])

        assert 'domain_relationship' in result
        assert result['domain_relationship'] == 'INVOKES'

    def test_enrich_edge_missing_nodes(self):
        """Test edge enrichment when nodes are missing"""
        enricher = DomainEnricher()

        graph = {"nodes": [], "edges": []}
        edge = {"source": "missing1", "target": "missing2", "type": "calls"}

        result = enricher.enrich_edge(edge, graph, context=[])

        # Should handle gracefully without crashing
        assert isinstance(result, dict)

    def test_process_full_graph(self, enriched_graph_layer2):
        """Test processing an entire graph"""
        enricher = DomainEnricher()
        result = enricher.process(enriched_graph_layer2, context=[])

        # All nodes should have layer3 enrichment
        for node in result['nodes']:
            assert 'enrichment' in node
            assert 'layer3' in node['enrichment']
            assert 'domain_concepts' in node['enrichment']['layer3']
            assert 'business_rules' in node['enrichment']['layer3']
            assert 'workflow_participation' in node['enrichment']['layer3']
            assert 'entity_relationships' in node['enrichment']['layer3']

        # All edges should have layer3 enrichment (even if empty)
        for edge in result['edges']:
            assert 'enrichment' in edge
            # Layer3 may add enrichment to edges or may not, depending on edge type
            # Just check that the edge has enrichment structure
            assert 'layer3' in edge['enrichment'] or 'layer2' in edge['enrichment']

    def test_context_usage(self, entity_graph):
        """Test that enricher can use context from previous iterations"""
        enricher = DomainEnricher()

        # Add layer2 enrichment
        for node in entity_graph['nodes']:
            node['enrichment'] = {
                'layer2': {
                    'patterns': [],
                    'naming_analysis': {'terms': []},
                    'method_roles': []
                }
            }

        # First iteration
        result1 = enricher.enrich_node(entity_graph['nodes'][0], entity_graph, context=[])

        # Second iteration with context
        context = [entity_graph]
        result2 = enricher.enrich_node(entity_graph['nodes'][0], entity_graph, context=context)

        # Both should produce valid results
        assert 'domain_concepts' in result1
        assert 'domain_concepts' in result2
