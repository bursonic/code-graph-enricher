#!/usr/bin/env python3
"""
Iterative Code Graph Enricher
Performs multiple passes of enrichment, each building on previous layers
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from abc import ABC, abstractmethod


class EnricherPass(ABC):
    """Base class for enrichment passes"""

    def __init__(self, layer_num: int, name: str):
        self.layer_num = layer_num
        self.name = name

    @abstractmethod
    def enrich_node(self, node: Dict[str, Any], graph: Dict[str, Any], context: List[Dict]) -> Dict[str, Any]:
        """Enrich a single node. Return enriched metadata to add to node."""
        pass

    @abstractmethod
    def enrich_edge(self, edge: Dict[str, Any], graph: Dict[str, Any], context: List[Dict]) -> Dict[str, Any]:
        """Enrich a single edge. Return enriched metadata to add to edge."""
        pass

    def process(self, graph: Dict[str, Any], context: List[Dict]) -> Dict[str, Any]:
        """Process entire graph, enriching all nodes and edges"""
        enriched_graph = json.loads(json.dumps(graph))  # Deep copy

        # Enrich nodes
        for i, node in enumerate(enriched_graph['nodes']):
            enrichment = self.enrich_node(node, enriched_graph, context)
            if enrichment:
                if 'enrichment' not in node:
                    node['enrichment'] = {}
                node['enrichment'][f'layer{self.layer_num}'] = enrichment

        # Enrich edges
        for i, edge in enumerate(enriched_graph['edges']):
            enrichment = self.enrich_edge(edge, enriched_graph, context)
            if enrichment:
                if 'enrichment' not in edge:
                    edge['enrichment'] = {}
                edge['enrichment'][f'layer{self.layer_num}'] = enrichment

        return enriched_graph


class IterativeEnricher:
    """Manages iterative enrichment pipeline"""

    def __init__(self, base_graph: Dict[str, Any], output_dir: Path):
        self.base_graph = base_graph
        self.output_dir = Path(output_dir)
        self.enrichers: List[EnricherPass] = []
        self.layers: List[Dict[str, Any]] = []

        # Create output directory structure
        self.enrichment_dir = self.output_dir / "enrichment"
        self.enrichment_dir.mkdir(parents=True, exist_ok=True)
        (self.enrichment_dir / "indexes").mkdir(exist_ok=True)

    def add_enricher(self, enricher: EnricherPass):
        """Add an enrichment pass to the pipeline"""
        self.enrichers.append(enricher)

    def _compute_hash(self, graph: Dict[str, Any]) -> str:
        """Compute hash of graph for convergence detection"""
        # Hash based on enrichment data only
        enrichments = []
        for node in graph.get('nodes', []):
            if 'enrichment' in node:
                enrichments.append(json.dumps(node['enrichment'], sort_keys=True))

        content = ''.join(sorted(enrichments))
        return hashlib.md5(content.encode()).hexdigest()

    def _save_layer(self, graph: Dict[str, Any], layer: int, enricher_name: str):
        """Save intermediate enrichment layer"""
        output_file = self.enrichment_dir / f"l{layer}-{enricher_name}.json"

        # Add metadata about this layer
        layer_graph = json.loads(json.dumps(graph))
        layer_graph['layer_metadata'] = {
            'layer': layer,
            'enricher': enricher_name,
            'generated': datetime.now().isoformat(),
            'node_count': len(graph['nodes']),
            'edge_count': len(graph['edges'])
        }

        with open(output_file, 'w') as f:
            json.dump(layer_graph, f, indent=2)

        print(f"  Saved layer {layer} to {output_file.name}")

    def _save_indexes(self, graph: Dict[str, Any]):
        """Generate and save lookup indexes"""
        indexes_dir = self.enrichment_dir / "indexes"

        # Entity index
        entity_index = {}
        for node in graph['nodes']:
            if node['type'] in ['class', 'function']:
                entity_index[node['id']] = {
                    'name': node['name'],
                    'type': node['type'],
                    'path': node['path'],
                    'location': node['location']
                }
                # Add enrichment summaries
                if 'enrichment' in node:
                    for layer, data in node['enrichment'].items():
                        if 'classification' in data:
                            entity_index[node['id']]['classification'] = data['classification']
                        if 'patterns' in data:
                            entity_index[node['id']]['patterns'] = data['patterns']

        with open(indexes_dir / "entity-index.json", 'w') as f:
            json.dump(entity_index, f, indent=2)

        print(f"  Generated entity index with {len(entity_index)} entries")

    def enrich(self, max_iterations: int = 4, convergence_check: bool = True) -> Dict[str, Any]:
        """
        Run enrichment pipeline

        Args:
            max_iterations: Maximum number of full pipeline iterations
            convergence_check: Stop early if graph stops changing

        Returns:
            Fully enriched graph
        """
        print(f"\nStarting iterative enrichment with {len(self.enrichers)} enrichers")
        print(f"Base graph: {len(self.base_graph['nodes'])} nodes, {len(self.base_graph['edges'])} edges")
        print()

        graph = json.loads(json.dumps(self.base_graph))  # Deep copy
        prev_hash = None

        for iteration in range(max_iterations):
            print(f"Iteration {iteration + 1}/{max_iterations}")

            iteration_changed = False

            # Apply each enricher in sequence
            for enricher in self.enrichers:
                print(f"  Applying {enricher.name}...")

                prev_graph_hash = self._compute_hash(graph)
                graph = enricher.process(graph, self.layers)
                new_graph_hash = self._compute_hash(graph)

                # Save this layer
                self._save_layer(graph, enricher.layer_num, enricher.name)

                if new_graph_hash != prev_graph_hash:
                    iteration_changed = True

            # Store this iteration's result
            self.layers.append(json.loads(json.dumps(graph)))

            # Check convergence
            current_hash = self._compute_hash(graph)
            if convergence_check and current_hash == prev_hash:
                print(f"\nConverged after iteration {iteration + 1}")
                break

            if not iteration_changed:
                print(f"\nNo changes in iteration {iteration + 1}, stopping")
                break

            prev_hash = current_hash

        # Generate indexes
        print("\nGenerating indexes...")
        self._save_indexes(graph)

        # Save final enriched graph
        final_path = self.output_dir / "code-graph-enriched.json"
        with open(final_path, 'w') as f:
            json.dump(graph, f, indent=2)

        print(f"\n✓ Final enriched graph saved to {final_path}")

        return graph

    def get_statistics(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics about enrichment"""
        stats = {
            'total_nodes': len(graph['nodes']),
            'total_edges': len(graph['edges']),
            'enriched_nodes': 0,
            'enrichments_by_layer': {},
            'classifications': {},
            'patterns': {}
        }

        for node in graph['nodes']:
            if 'enrichment' in node:
                stats['enriched_nodes'] += 1

                for layer, data in node['enrichment'].items():
                    stats['enrichments_by_layer'][layer] = \
                        stats['enrichments_by_layer'].get(layer, 0) + 1

                    # Collect classifications
                    if 'classification' in data:
                        cls = data['classification']
                        stats['classifications'][cls] = \
                            stats['classifications'].get(cls, 0) + 1

                    # Collect patterns
                    if 'patterns' in data:
                        for pattern in data['patterns']:
                            stats['patterns'][pattern] = \
                                stats['patterns'].get(pattern, 0) + 1

        return stats
