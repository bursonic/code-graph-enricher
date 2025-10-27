#!/usr/bin/env python3
"""
Layer 1: Structural Enrichment
Adds classification, complexity metrics, and dependency information
"""

from pathlib import Path
from typing import Dict, List, Any
from iterative_enricher import EnricherPass


class StructuralEnricher(EnricherPass):
    """Layer 1: Structural analysis and classification"""

    def __init__(self, root_path: Path):
        super().__init__(layer_num=1, name="structural")
        self.root_path = Path(root_path)

    def _classify_by_name(self, name: str, node_type: str) -> str:
        """Classify node based on naming patterns"""
        name_lower = name.lower()

        # Infrastructure indicators
        infra_patterns = [
            'config', 'settings', 'setup', 'init', 'main',
            'utils', 'helper', 'base', 'abstract',
            'test', 'mock', 'fixture'
        ]

        # Domain indicators
        domain_patterns = [
            'user', 'product', 'order', 'cart', 'payment',
            'customer', 'account', 'invoice', 'item',
            'service', 'repository', 'model', 'entity'
        ]

        # Check infrastructure patterns
        for pattern in infra_patterns:
            if pattern in name_lower:
                return 'infrastructure'

        # Check domain patterns
        for pattern in domain_patterns:
            if pattern in name_lower:
                return 'domain'

        # Files are more likely infrastructure
        if node_type == 'file':
            return 'infrastructure'

        # Classes are more likely domain
        if node_type == 'class':
            return 'domain'

        return 'unknown'

    def _classify_by_imports(self, node: Dict[str, Any], graph: Dict[str, Any]) -> str:
        """Classify based on what the node imports"""
        if node['type'] != 'file':
            return None

        imports = node.get('metadata', {}).get('imports', [])
        if not imports:
            return None

        # Standard library imports suggest infrastructure
        stdlib_imports = ['os', 'sys', 'json', 'logging', 'typing', 'datetime', 'pathlib']
        domain_imports = []

        for imp in imports:
            if imp in stdlib_imports:
                continue
            # Local imports are likely domain
            domain_imports.append(imp)

        # If mostly standard lib, likely infrastructure
        if len(domain_imports) == 0 and len(imports) > 0:
            return 'infrastructure'

        # If has domain imports, likely domain or mixed
        if len(domain_imports) > 0:
            return 'domain' if len(domain_imports) > len(imports) / 2 else 'mixed'

        return None

    def _calculate_complexity(self, node: Dict[str, Any], graph: Dict[str, Any]) -> Dict[str, int]:
        """Calculate complexity metrics for a node"""
        complexity = {
            'loc': 0,
            'nesting_depth': 0,
            'num_params': 0,
            'num_methods': 0
        }

        # Try to read source file and count lines
        try:
            file_path = self.root_path / node['path']
            if file_path.exists():
                with open(file_path, 'r') as f:
                    lines = f.readlines()

                # For files, count all lines
                if node['type'] == 'file':
                    complexity['loc'] = len([l for l in lines if l.strip() and not l.strip().startswith('#')])

                # For classes/functions, estimate based on typical sizes
                elif node['type'] == 'class':
                    # Count methods contained in this class
                    for edge in graph['edges']:
                        if edge['source'] == node['id'] and edge['type'] == 'contains':
                            complexity['num_methods'] += 1

                    # Estimate LOC (rough heuristic)
                    complexity['loc'] = complexity['num_methods'] * 5 + 10

                elif node['type'] == 'function':
                    # Estimate function LOC (rough heuristic for PoC)
                    complexity['loc'] = 10  # Default estimate
                    complexity['nesting_depth'] = 1  # Placeholder

        except Exception as e:
            pass  # Keep default values

        return complexity

    def _calculate_dependencies(self, node: Dict[str, Any], graph: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate dependency metrics"""
        deps = {
            'import_depth': 0,
            'num_imports': 0,
            'imports_from': []
        }

        if node['type'] == 'file':
            imports = node.get('metadata', {}).get('imports', [])
            deps['num_imports'] = len(imports)
            deps['imports_from'] = imports

            # Calculate import depth (how many levels of dependencies)
            # For PoC, just check if imports are stdlib (depth 0) or local (depth 1)
            stdlib_imports = ['os', 'sys', 'json', 'logging', 'typing', 'datetime', 'pathlib', 'dataclasses']
            local_imports = [imp for imp in imports if imp not in stdlib_imports]

            if local_imports:
                deps['import_depth'] = 1
            else:
                deps['import_depth'] = 0

        return deps

    def enrich_node(self, node: Dict[str, Any], graph: Dict[str, Any], context: List[Dict]) -> Dict[str, Any]:
        """Add structural enrichment to node"""
        enrichment = {}

        # Classification
        name_classification = self._classify_by_name(node['name'], node['type'])
        import_classification = self._classify_by_imports(node, graph)

        # Combine classifications (import-based takes precedence if available)
        if import_classification:
            enrichment['classification'] = import_classification
        else:
            enrichment['classification'] = name_classification

        # Complexity metrics
        enrichment['complexity'] = self._calculate_complexity(node, graph)

        # Dependency analysis
        enrichment['dependencies'] = self._calculate_dependencies(node, graph)

        return enrichment

    def enrich_edge(self, edge: Dict[str, Any], graph: Dict[str, Any], context: List[Dict]) -> Dict[str, Any]:
        """Add structural enrichment to edge"""
        enrichment = {}

        # Add edge weight (for now, all edges have weight 1.0)
        enrichment['weight'] = 1.0

        # Calculate depth from entry point (for PoC, simplified)
        enrichment['depth'] = 1

        return enrichment
