#!/usr/bin/env python3
"""
Tests for CLI functionality
"""

import pytest
import json
import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch
from enricher.cli import load_graph, print_statistics, main


class TestLoadGraph:
    """Test the load_graph function"""

    def test_load_valid_graph(self, temp_output_dir, sample_graph):
        """Test loading a valid graph file"""
        graph_file = temp_output_dir / "test-graph.json"
        with open(graph_file, 'w') as f:
            json.dump(sample_graph, f)

        result = load_graph(graph_file)

        assert result == sample_graph
        assert 'nodes' in result
        assert 'edges' in result

    def test_load_missing_file(self, temp_output_dir):
        """Test loading a non-existent file"""
        missing_file = temp_output_dir / "missing.json"

        with pytest.raises(SystemExit) as exc_info:
            load_graph(missing_file)

        assert exc_info.value.code == 1

    def test_load_invalid_json(self, temp_output_dir):
        """Test loading a file with invalid JSON"""
        invalid_file = temp_output_dir / "invalid.json"
        invalid_file.write_text("{ invalid json }")

        with pytest.raises(SystemExit) as exc_info:
            load_graph(invalid_file)

        assert exc_info.value.code == 1


class TestPrintStatistics:
    """Test the print_statistics function"""

    def test_print_statistics_basic(self, capsys):
        """Test printing basic statistics"""
        stats = {
            'total_nodes': 10,
            'enriched_nodes': 8,
            'enrichments_by_layer': {
                'layer1': 8,
                'layer2': 8,
                'layer3': 8
            },
            'classifications': {
                'domain': 5,
                'infrastructure': 3
            },
            'patterns': {
                'Entity': 3,
                'Service': 2,
                'Repository': 1
            }
        }

        print_statistics(stats)

        captured = capsys.readouterr()
        output = captured.out

        # Check key information is present
        assert "Total nodes: 10" in output
        assert "Enriched nodes: 8" in output
        assert "layer1: 8" in output
        assert "layer2: 8" in output
        assert "layer3: 8" in output
        assert "domain: 5" in output
        assert "infrastructure: 3" in output
        assert "Entity: 3" in output
        assert "Service: 2" in output
        assert "Repository: 1" in output

    def test_print_statistics_empty(self, capsys):
        """Test printing statistics with empty data"""
        stats = {
            'total_nodes': 0,
            'enriched_nodes': 0,
            'enrichments_by_layer': {},
            'classifications': {},
            'patterns': {}
        }

        print_statistics(stats)

        captured = capsys.readouterr()
        output = captured.out

        # Should still print basic structure without crashing
        assert "Total nodes: 0" in output
        assert "Enriched nodes: 0" in output

    def test_print_statistics_patterns_sorted(self, capsys):
        """Test that patterns are sorted by count (descending)"""
        stats = {
            'total_nodes': 10,
            'enriched_nodes': 10,
            'enrichments_by_layer': {},
            'classifications': {},
            'patterns': {
                'Entity': 1,
                'Service': 5,
                'Repository': 3
            }
        }

        print_statistics(stats)

        captured = capsys.readouterr()
        output = captured.out

        # Service (5) should appear before Repository (3), which should appear before Entity (1)
        service_pos = output.find("Service: 5")
        repo_pos = output.find("Repository: 3")
        entity_pos = output.find("Entity: 1")

        assert service_pos < repo_pos < entity_pos


class TestMain:
    """Test the main CLI function"""

    def test_main_no_args(self):
        """Test CLI with no arguments shows help"""
        with patch.object(sys, 'argv', ['enrich-graph']):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

    def test_main_help_output(self, capsys):
        """Test that help message is displayed with no args"""
        with patch.object(sys, 'argv', ['enrich-graph']):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        output = captured.out

        assert "Code Graph Enricher" in output
        assert "Usage:" in output
        assert "graph_json_path" in output
        assert "root_code_path" in output
        assert "--iterations" in output
        assert "--no-convergence" in output

    def test_main_basic_execution(self, temp_output_dir, sample_graph, temp_source_dir):
        """Test basic CLI execution with graph file"""
        # Create graph file
        graph_file = temp_output_dir / "code-graph.json"
        with open(graph_file, 'w') as f:
            json.dump(sample_graph, f)

        # Run CLI
        with patch.object(sys, 'argv', [
            'enrich-graph',
            str(graph_file),
            str(temp_source_dir)
        ]):
            main()

        # Check output files were created
        assert (temp_output_dir / "code-graph-enriched.json").exists()
        assert (temp_output_dir / "enrichment" / "l1-structural.json").exists()
        assert (temp_output_dir / "enrichment" / "l2-semantic.json").exists()
        assert (temp_output_dir / "enrichment" / "l3-domain.json").exists()
        assert (temp_output_dir / "enrichment" / "indexes" / "entity-index.json").exists()

    def test_main_with_iterations_option(self, temp_output_dir, sample_graph, temp_source_dir):
        """Test CLI with custom iterations count"""
        graph_file = temp_output_dir / "code-graph.json"
        with open(graph_file, 'w') as f:
            json.dump(sample_graph, f)

        with patch.object(sys, 'argv', [
            'enrich-graph',
            str(graph_file),
            str(temp_source_dir),
            '--iterations', '3'
        ]):
            main()

        # Check output was created
        assert (temp_output_dir / "code-graph-enriched.json").exists()

    def test_main_with_no_convergence_option(self, temp_output_dir, sample_graph, temp_source_dir):
        """Test CLI with convergence check disabled"""
        graph_file = temp_output_dir / "code-graph.json"
        with open(graph_file, 'w') as f:
            json.dump(sample_graph, f)

        with patch.object(sys, 'argv', [
            'enrich-graph',
            str(graph_file),
            str(temp_source_dir),
            '--no-convergence'
        ]):
            main()

        # Check output was created
        assert (temp_output_dir / "code-graph-enriched.json").exists()

    def test_main_default_root_path(self, temp_output_dir, sample_graph):
        """Test CLI with default root path (inferred from graph location)"""
        # Create graph in a subdirectory to simulate .ai-gov structure
        ai_gov_dir = temp_output_dir / ".ai-gov"
        ai_gov_dir.mkdir()

        graph_file = ai_gov_dir / "code-graph.json"
        with open(graph_file, 'w') as f:
            json.dump(sample_graph, f)

        with patch.object(sys, 'argv', [
            'enrich-graph',
            str(graph_file)
        ]):
            main()

        # Check output was created
        assert (ai_gov_dir / "code-graph-enriched.json").exists()

    def test_main_combined_options(self, temp_output_dir, sample_graph, temp_source_dir):
        """Test CLI with multiple options combined"""
        graph_file = temp_output_dir / "code-graph.json"
        with open(graph_file, 'w') as f:
            json.dump(sample_graph, f)

        with patch.object(sys, 'argv', [
            'enrich-graph',
            str(graph_file),
            str(temp_source_dir),
            '--iterations', '4',
            '--no-convergence'
        ]):
            main()

        # Check output was created
        assert (temp_output_dir / "code-graph-enriched.json").exists()

    def test_main_enriched_graph_content(self, temp_output_dir, sample_graph, temp_source_dir):
        """Test that enriched graph has correct structure"""
        graph_file = temp_output_dir / "code-graph.json"
        with open(graph_file, 'w') as f:
            json.dump(sample_graph, f)

        with patch.object(sys, 'argv', [
            'enrich-graph',
            str(graph_file),
            str(temp_source_dir)
        ]):
            main()

        # Load enriched graph
        enriched_file = temp_output_dir / "code-graph-enriched.json"
        with open(enriched_file) as f:
            enriched = json.load(f)

        # Check structure
        assert 'nodes' in enriched
        assert 'edges' in enriched
        assert len(enriched['nodes']) == len(sample_graph['nodes'])

        # Check that nodes have enrichment
        for node in enriched['nodes']:
            assert 'enrichment' in node
            assert 'layer1' in node['enrichment']
            assert 'layer2' in node['enrichment']
            assert 'layer3' in node['enrichment']

    def test_main_output_messages(self, capsys, temp_output_dir, sample_graph, temp_source_dir):
        """Test that CLI prints appropriate messages"""
        graph_file = temp_output_dir / "code-graph.json"
        with open(graph_file, 'w') as f:
            json.dump(sample_graph, f)

        with patch.object(sys, 'argv', [
            'enrich-graph',
            str(graph_file),
            str(temp_source_dir)
        ]):
            main()

        captured = capsys.readouterr()
        output = captured.out

        # Check key messages
        assert "Code Graph Enricher" in output
        assert "Loading graph..." in output
        assert "Loaded" in output
        assert "Configuring enrichment pipeline..." in output
        assert "Layer 1: Structural enrichment" in output
        assert "Layer 2: Semantic enrichment" in output
        assert "Layer 3: Domain enrichment" in output
        assert "ENRICHMENT STATISTICS" in output
        assert "Enrichment complete!" in output
        assert "Output files:" in output

    def test_main_invalid_iterations_value(self, temp_output_dir, sample_graph, temp_source_dir):
        """Test CLI with invalid iterations value"""
        graph_file = temp_output_dir / "code-graph.json"
        with open(graph_file, 'w') as f:
            json.dump(sample_graph, f)

        # Should raise ValueError or similar when trying to convert "invalid" to int
        with patch.object(sys, 'argv', [
            'enrich-graph',
            str(graph_file),
            str(temp_source_dir),
            '--iterations', 'invalid'
        ]):
            with pytest.raises(ValueError):
                main()

    def test_main_relative_paths(self, temp_output_dir, sample_graph, temp_source_dir):
        """Test CLI with relative paths (converted to absolute)"""
        graph_file = temp_output_dir / "code-graph.json"
        with open(graph_file, 'w') as f:
            json.dump(sample_graph, f)

        # Use relative path
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(temp_output_dir.parent)

            relative_graph = Path(temp_output_dir.name) / "code-graph.json"
            relative_source = Path(temp_source_dir.name) if temp_source_dir.parent == Path.cwd() else temp_source_dir

            with patch.object(sys, 'argv', [
                'enrich-graph',
                str(relative_graph),
                str(temp_source_dir)
            ]):
                main()

            # Check output was created
            assert (temp_output_dir / "code-graph-enriched.json").exists()
        finally:
            import os
            os.chdir(original_cwd)
