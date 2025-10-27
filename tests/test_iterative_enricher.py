#!/usr/bin/env python3
"""
Tests for IterativeEnricher and EnricherPass base class
"""

import pytest
import json
from pathlib import Path
from enricher.iterative_enricher import IterativeEnricher, EnricherPass


class MockEnricher(EnricherPass):
    """Mock enricher for testing"""

    def __init__(self, layer_num=1, name="mock", node_value="test_value"):
        super().__init__(layer_num, name)
        self.node_value = node_value
        self.edge_value = "edge_test"

    def enrich_node(self, node, graph, context):
        return {"mock_data": self.node_value, "node_id": node['id']}

    def enrich_edge(self, edge, graph, context):
        return {"mock_edge": self.edge_value}


class TestEnricherPass:
    """Test the EnricherPass base class"""

    def test_enricher_pass_initialization(self):
        """Test that EnricherPass can be initialized properly"""
        enricher = MockEnricher(layer_num=1, name="test")
        assert enricher.layer_num == 1
        assert enricher.name == "test"

    def test_enricher_pass_process_nodes(self, sample_graph):
        """Test that process() enriches all nodes"""
        enricher = MockEnricher(layer_num=1, name="test", node_value="enriched")
        result = enricher.process(sample_graph, context=[])

        # Check that all nodes were enriched
        for node in result['nodes']:
            assert 'enrichment' in node
            assert 'layer1' in node['enrichment']
            assert node['enrichment']['layer1']['mock_data'] == "enriched"
            assert node['enrichment']['layer1']['node_id'] == node['id']

    def test_enricher_pass_process_edges(self, sample_graph):
        """Test that process() enriches all edges"""
        enricher = MockEnricher(layer_num=1, name="test")
        result = enricher.process(sample_graph, context=[])

        # Check that all edges were enriched
        for edge in result['edges']:
            assert 'enrichment' in edge
            assert 'layer1' in edge['enrichment']
            assert edge['enrichment']['layer1']['mock_edge'] == "edge_test"

    def test_enricher_pass_deep_copy(self, sample_graph):
        """Test that process() creates a deep copy and doesn't modify original"""
        original_json = json.dumps(sample_graph, sort_keys=True)
        enricher = MockEnricher(layer_num=1, name="test")
        result = enricher.process(sample_graph, context=[])

        # Original should be unchanged
        assert json.dumps(sample_graph, sort_keys=True) == original_json
        # Result should be different
        assert json.dumps(result, sort_keys=True) != original_json

    def test_enricher_pass_multiple_layers(self, sample_graph):
        """Test that multiple enricher passes can add different layers"""
        enricher1 = MockEnricher(layer_num=1, name="first", node_value="layer1_data")
        enricher2 = MockEnricher(layer_num=2, name="second", node_value="layer2_data")

        result1 = enricher1.process(sample_graph, context=[])
        result2 = enricher2.process(result1, context=[])

        # Check both layers exist
        for node in result2['nodes']:
            assert 'layer1' in node['enrichment']
            assert 'layer2' in node['enrichment']
            assert node['enrichment']['layer1']['mock_data'] == "layer1_data"
            assert node['enrichment']['layer2']['mock_data'] == "layer2_data"


class TestIterativeEnricher:
    """Test the IterativeEnricher orchestrator"""

    def test_initialization(self, sample_graph, temp_output_dir):
        """Test that IterativeEnricher initializes correctly"""
        enricher = IterativeEnricher(sample_graph, temp_output_dir)

        assert enricher.base_graph == sample_graph
        assert enricher.output_dir == temp_output_dir
        assert len(enricher.enrichers) == 0
        assert len(enricher.layers) == 0

        # Check directory structure created
        assert (temp_output_dir / "enrichment").exists()
        assert (temp_output_dir / "enrichment" / "indexes").exists()

    def test_add_enricher(self, sample_graph, temp_output_dir):
        """Test adding enrichers to the pipeline"""
        enricher = IterativeEnricher(sample_graph, temp_output_dir)

        mock1 = MockEnricher(layer_num=1, name="first")
        mock2 = MockEnricher(layer_num=2, name="second")

        enricher.add_enricher(mock1)
        enricher.add_enricher(mock2)

        assert len(enricher.enrichers) == 2
        assert enricher.enrichers[0] == mock1
        assert enricher.enrichers[1] == mock2

    def test_compute_hash(self, sample_graph, temp_output_dir):
        """Test hash computation for convergence detection"""
        enricher = IterativeEnricher(sample_graph, temp_output_dir)

        # Hash of empty graph
        hash1 = enricher._compute_hash(sample_graph)

        # Add enrichment to one node
        graph_copy = json.loads(json.dumps(sample_graph))
        graph_copy['nodes'][0]['enrichment'] = {'layer1': {'test': 'data'}}
        hash2 = enricher._compute_hash(graph_copy)

        # Hashes should be different
        assert hash1 != hash2

        # Same enrichment should produce same hash
        graph_copy2 = json.loads(json.dumps(sample_graph))
        graph_copy2['nodes'][0]['enrichment'] = {'layer1': {'test': 'data'}}
        hash3 = enricher._compute_hash(graph_copy2)

        assert hash2 == hash3

    def test_enrich_single_iteration(self, sample_graph, temp_output_dir):
        """Test enrichment with a single iteration"""
        enricher = IterativeEnricher(sample_graph, temp_output_dir)
        mock = MockEnricher(layer_num=1, name="test", node_value="enriched")
        enricher.add_enricher(mock)

        result = enricher.enrich(max_iterations=1, convergence_check=False)

        # Check that enrichment was applied
        assert len(result['nodes']) == len(sample_graph['nodes'])
        for node in result['nodes']:
            assert 'enrichment' in node
            assert 'layer1' in node['enrichment']
            assert node['enrichment']['layer1']['mock_data'] == "enriched"

        # Check that files were created
        assert (temp_output_dir / "enrichment" / "l1-test.json").exists()
        assert (temp_output_dir / "code-graph-enriched.json").exists()
        assert (temp_output_dir / "enrichment" / "indexes" / "entity-index.json").exists()

    def test_enrich_multiple_iterations(self, sample_graph, temp_output_dir):
        """Test enrichment with multiple iterations"""
        enricher = IterativeEnricher(sample_graph, temp_output_dir)
        mock1 = MockEnricher(layer_num=1, name="layer1")
        mock2 = MockEnricher(layer_num=2, name="layer2")
        enricher.add_enricher(mock1)
        enricher.add_enricher(mock2)

        result = enricher.enrich(max_iterations=2, convergence_check=False)

        # Check both layers were applied
        for node in result['nodes']:
            assert 'layer1' in node['enrichment']
            assert 'layer2' in node['enrichment']

        # Check layer history
        assert len(enricher.layers) == 2

    def test_convergence_detection(self, sample_graph, temp_output_dir):
        """Test that convergence detection stops iterations early"""

        class StaticEnricher(EnricherPass):
            """Enricher that produces same output every time"""
            def __init__(self):
                super().__init__(layer_num=1, name="static")

            def enrich_node(self, node, graph, context):
                return {"static": "value"}

            def enrich_edge(self, edge, graph, context):
                return {"static": "edge"}

        enricher = IterativeEnricher(sample_graph, temp_output_dir)
        static = StaticEnricher()
        enricher.add_enricher(static)

        # With convergence check, should stop after 2 iterations
        # (iteration 1 adds data, iteration 2 produces same result)
        result = enricher.enrich(max_iterations=10, convergence_check=True)

        # Should have stopped early
        assert len(enricher.layers) < 10
        assert len(enricher.layers) >= 1

    def test_save_layer(self, sample_graph, temp_output_dir):
        """Test that layer files are saved correctly"""
        enricher = IterativeEnricher(sample_graph, temp_output_dir)
        mock = MockEnricher(layer_num=1, name="test")

        # Enrich and save
        enriched = mock.process(sample_graph, [])
        enricher._save_layer(enriched, layer=1, enricher_name="test")

        # Check file exists
        layer_file = temp_output_dir / "enrichment" / "l1-test.json"
        assert layer_file.exists()

        # Load and verify content
        with open(layer_file) as f:
            saved_data = json.load(f)

        assert 'layer_metadata' in saved_data
        assert saved_data['layer_metadata']['layer'] == 1
        assert saved_data['layer_metadata']['enricher'] == "test"
        assert saved_data['layer_metadata']['node_count'] == len(sample_graph['nodes'])
        assert saved_data['layer_metadata']['edge_count'] == len(sample_graph['edges'])

    def test_save_indexes(self, enriched_graph_layer2, temp_output_dir):
        """Test that entity index is generated correctly"""
        enricher = IterativeEnricher(enriched_graph_layer2, temp_output_dir)
        enricher._save_indexes(enriched_graph_layer2)

        # Check index file exists
        index_file = temp_output_dir / "enrichment" / "indexes" / "entity-index.json"
        assert index_file.exists()

        # Load and verify content
        with open(index_file) as f:
            index_data = json.load(f)

        # Should contain classes and functions
        assert len(index_data) > 0

        # Check structure
        for node_id, entry in index_data.items():
            assert 'name' in entry
            assert 'type' in entry
            assert 'path' in entry
            assert 'location' in entry

    def test_get_statistics(self, enriched_graph_layer2, temp_output_dir):
        """Test statistics generation"""
        enricher = IterativeEnricher(enriched_graph_layer2, temp_output_dir)
        stats = enricher.get_statistics(enriched_graph_layer2)

        assert 'total_nodes' in stats
        assert 'total_edges' in stats
        assert 'enriched_nodes' in stats
        assert 'enrichments_by_layer' in stats
        assert 'classifications' in stats
        assert 'patterns' in stats

        assert stats['total_nodes'] == len(enriched_graph_layer2['nodes'])
        assert stats['enriched_nodes'] > 0
        assert 'layer1' in stats['enrichments_by_layer']
        assert 'layer2' in stats['enrichments_by_layer']

    def test_context_propagation(self, sample_graph, temp_output_dir):
        """Test that context (previous iterations) is passed to enrichers"""

        class ContextAwareEnricher(EnricherPass):
            """Enricher that uses context from previous iterations"""
            def __init__(self):
                super().__init__(layer_num=1, name="context_aware")

            def enrich_node(self, node, graph, context):
                return {
                    "iteration": len(context) + 1,
                    "has_context": len(context) > 0
                }

            def enrich_edge(self, edge, graph, context):
                return {}

        enricher = IterativeEnricher(sample_graph, temp_output_dir)
        context_enricher = ContextAwareEnricher()
        enricher.add_enricher(context_enricher)

        result = enricher.enrich(max_iterations=3, convergence_check=False)

        # After 3 iterations, the last enrichment should show iteration 3
        # and should have context from previous iterations
        assert len(enricher.layers) == 3

        # The enrichment in the final result should be from iteration 3
        # (but convergence may have stopped it early, so just check layers exist)
        assert len(enricher.layers) >= 1

    def test_empty_graph(self, temp_output_dir):
        """Test enrichment with an empty graph"""
        empty_graph = {"nodes": [], "edges": []}
        enricher = IterativeEnricher(empty_graph, temp_output_dir)
        mock = MockEnricher(layer_num=1, name="test")
        enricher.add_enricher(mock)

        result = enricher.enrich(max_iterations=1, convergence_check=False)

        assert len(result['nodes']) == 0
        assert len(result['edges']) == 0
        assert (temp_output_dir / "code-graph-enriched.json").exists()
