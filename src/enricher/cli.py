#!/usr/bin/env python3
"""
Code Graph Enricher - CLI Tool
Performs iterative enrichment of code graphs with structural, semantic, and domain knowledge
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

from .iterative_enricher import IterativeEnricher
from .layer1_structural import StructuralEnricher
from .layer2_semantic import SemanticEnricher
from .layer3_domain import DomainEnricher


def load_graph(graph_path: Path) -> Dict[str, Any]:
    """Load code graph from JSON file"""
    try:
        with open(graph_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Graph file not found at {graph_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in graph file: {e}", file=sys.stderr)
        sys.exit(1)


def print_statistics(stats: Dict[str, Any]):
    """Pretty print enrichment statistics"""
    print("\n" + "="*60)
    print("ENRICHMENT STATISTICS")
    print("="*60)

    print(f"\nTotal nodes: {stats['total_nodes']}")
    print(f"Enriched nodes: {stats['enriched_nodes']}")

    if stats['enrichments_by_layer']:
        print("\nEnrichments by layer:")
        for layer, count in sorted(stats['enrichments_by_layer'].items()):
            print(f"  {layer}: {count} nodes")

    if stats['classifications']:
        print("\nNode classifications:")
        for classification, count in sorted(stats['classifications'].items()):
            print(f"  {classification}: {count}")

    if stats['patterns']:
        print("\nDetected patterns:")
        for pattern, count in sorted(stats['patterns'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {pattern}: {count}")

    print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        prog='enrich-graph',
        description='Performs iterative enrichment of code graphs with structural, semantic, and domain knowledge',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Description:
  Performs iterative enrichment of a code graph with:
    - Layer 1: Structural analysis (classification, complexity, dependencies)
    - Layer 2: Semantic analysis (patterns, naming conventions)
    - Layer 3: Domain extraction (entities, business rules, workflows)

Output:
  Creates enrichment/ directory with intermediate layers and indexes
  Saves final enriched graph as code-graph-enriched.json

Examples:
  enrich-graph ./code-graph.json ./src
  enrich-graph ./code-graph.json ./src --iterations 3
  enrich-graph ./code-graph.json --no-convergence
"""
    )

    parser.add_argument(
        'graph_json_path',
        type=Path,
        help='Path to code-graph.json file'
    )

    parser.add_argument(
        'root_code_path',
        type=Path,
        nargs='?',
        help='Root directory of source code (default: auto-detect from graph path)'
    )

    parser.add_argument(
        '--iterations',
        type=int,
        default=2,
        metavar='N',
        help='Maximum number of enrichment iterations (default: 2)'
    )

    parser.add_argument(
        '--no-convergence',
        action='store_true',
        help='Disable early stopping on convergence'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='Code Graph Enricher v0.1.0'
    )

    args = parser.parse_args()

    # Resolve paths
    graph_path = args.graph_json_path.resolve()

    if args.root_code_path:
        root_path = args.root_code_path.resolve()
    else:
        # Default: assume graph is in .ai-gov/ subdirectory
        root_path = graph_path.parent.parent

    max_iterations = args.iterations
    convergence_check = not args.no_convergence

    print(f"Code Graph Enricher v0.1.0")
    print(f"{'='*60}")
    print(f"Graph file: {graph_path}")
    print(f"Root code path: {root_path}")
    print(f"Max iterations: {max_iterations}")
    print(f"Convergence check: {'enabled' if convergence_check else 'disabled'}")

    # Load base graph
    print(f"\nLoading graph...")
    base_graph = load_graph(graph_path)
    print(f"Loaded {len(base_graph['nodes'])} nodes, {len(base_graph['edges'])} edges")

    # Create enricher
    output_dir = graph_path.parent
    enricher = IterativeEnricher(base_graph, output_dir)

    # Add enrichment passes
    print("\nConfiguring enrichment pipeline...")
    print("  Layer 1: Structural enrichment")
    enricher.add_enricher(StructuralEnricher(root_path))

    print("  Layer 2: Semantic enrichment")
    enricher.add_enricher(SemanticEnricher())

    print("  Layer 3: Domain enrichment")
    enricher.add_enricher(DomainEnricher())

    # Run enrichment
    enriched_graph = enricher.enrich(
        max_iterations=max_iterations,
        convergence_check=convergence_check
    )

    # Print statistics
    stats = enricher.get_statistics(enriched_graph)
    print_statistics(stats)

    print("\n✓ Enrichment complete!")
    print(f"\nOutput files:")
    print(f"  Final graph: {output_dir}/code-graph-enriched.json")
    print(f"  Layer artifacts: {output_dir}/enrichment/l*.json")
    print(f"  Indexes: {output_dir}/enrichment/indexes/*.json")


if __name__ == "__main__":
    main()
