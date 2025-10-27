#!/usr/bin/env python3
"""
Layer 2: Semantic Enrichment
Detects patterns, analyzes naming, classifies method roles
"""

import re
from typing import Dict, List, Any, Set
from iterative_enricher import EnricherPass


class SemanticEnricher(EnricherPass):
    """Layer 2: Semantic analysis - patterns and naming"""

    def __init__(self):
        super().__init__(layer_num=2, name="semantic")

    def _detect_patterns(self, node: Dict[str, Any], graph: Dict[str, Any], context: List[Dict]) -> List[str]:
        """Detect design patterns based on structure and naming"""
        patterns = []

        if node['type'] == 'class':
            name = node['name']
            name_lower = name.lower()

            # Entity pattern: typically dataclasses or simple models
            if any(term in name_lower for term in ['user', 'product', 'order', 'item', 'customer']):
                patterns.append('Entity')

            # Value Object pattern: immutable, dataclass-like
            if 'value' in name_lower or node.get('metadata', {}).get('is_dataclass', False):
                patterns.append('ValueObject')

            # Service pattern
            if 'service' in name_lower:
                patterns.append('Service')

            # Repository pattern
            if 'repository' in name_lower or 'repo' in name_lower:
                patterns.append('Repository')

            # Factory pattern
            if 'factory' in name_lower or 'builder' in name_lower:
                patterns.append('Factory')

            # Data Transfer Object
            if 'dto' in name_lower or name.endswith('DTO'):
                patterns.append('DTO')

        elif node['type'] == 'function':
            name = node['name']
            name_lower = name.lower()

            # Factory function pattern
            if name.startswith('create_') or name.startswith('make_') or name.startswith('build_'):
                patterns.append('FactoryFunction')

            # Strategy pattern (function-based)
            if name.endswith('_strategy') or 'strategy' in name_lower:
                patterns.append('Strategy')

        return patterns

    def _analyze_naming(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze naming conventions and extract terms"""
        name = node['name']

        analysis = {
            'terms': [],
            'conventions': '',
            'role_indicators': []
        }

        # Detect naming convention
        if '_' in name:
            analysis['conventions'] = 'snake_case'
        elif name[0].isupper():
            analysis['conventions'] = 'PascalCase'
        elif name[0].islower() and any(c.isupper() for c in name[1:]):
            analysis['conventions'] = 'camelCase'
        else:
            analysis['conventions'] = 'unknown'

        # Extract terms (split by underscore or camelCase)
        if analysis['conventions'] == 'snake_case':
            terms = name.split('_')
        elif analysis['conventions'] in ['camelCase', 'PascalCase']:
            # Split camelCase: insertBefore -> ['insert', 'Before']
            terms = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)', name)
        else:
            terms = [name]

        analysis['terms'] = [t.lower() for t in terms if t]

        # Detect role indicators
        role_prefixes = ['get', 'set', 'is', 'has', 'can', 'should', 'calculate', 'compute',
                         'validate', 'check', 'create', 'build', 'make', 'add', 'remove',
                         'update', 'delete', 'find', 'search', 'filter', 'transform',
                         'process', 'handle', 'format', 'parse', 'apply']

        for prefix in role_prefixes:
            if any(term.startswith(prefix) for term in analysis['terms']):
                if prefix not in analysis['role_indicators']:
                    analysis['role_indicators'].append(prefix)

        return analysis

    def _classify_method_role(self, node: Dict[str, Any], naming: Dict[str, Any]) -> List[str]:
        """Classify the role of a method/function"""
        if node['type'] != 'function':
            return []

        roles = []
        name = node['name'].lower()
        indicators = naming.get('role_indicators', [])

        # Getter
        if any(ind in ['get', 'fetch', 'retrieve', 'find'] for ind in indicators):
            roles.append('getter')

        # Setter
        if any(ind in ['set', 'update', 'assign'] for ind in indicators):
            roles.append('setter')

        # Validator
        if any(ind in ['validate', 'check', 'verify', 'is', 'has', 'can'] for ind in indicators):
            roles.append('validator')

        # Calculator/Computer
        if any(ind in ['calculate', 'compute', 'sum', 'total', 'average'] for ind in indicators):
            roles.append('calculator')

        # Transformer
        if any(ind in ['transform', 'convert', 'format', 'parse', 'process'] for ind in indicators):
            roles.append('transformer')

        # Creator
        if any(ind in ['create', 'build', 'make', 'generate'] for ind in indicators):
            roles.append('creator')

        # Mutator (add/remove)
        if any(ind in ['add', 'remove', 'delete', 'insert', 'append'] for ind in indicators):
            roles.append('mutator')

        # If no specific role, mark as general
        if not roles:
            roles.append('general')

        return roles

    def _determine_api_surface(self, node: Dict[str, Any]) -> str:
        """Determine if node is public, private, or protected"""
        name = node['name']

        # Python convention: single underscore = protected, double = private
        if name.startswith('__') and not name.endswith('__'):
            return 'private'
        elif name.startswith('_'):
            return 'protected'
        else:
            return 'public'

    def enrich_node(self, node: Dict[str, Any], graph: Dict[str, Any], context: List[Dict]) -> Dict[str, Any]:
        """Add semantic enrichment to node"""
        enrichment = {}

        # Pattern detection (uses Layer 1 classification if available)
        enrichment['patterns'] = self._detect_patterns(node, graph, context)

        # Naming analysis
        enrichment['naming_analysis'] = self._analyze_naming(node)

        # Method role classification
        enrichment['method_roles'] = self._classify_method_role(node, enrichment['naming_analysis'])

        # API surface determination
        enrichment['api_surface'] = self._determine_api_surface(node)

        return enrichment

    def enrich_edge(self, edge: Dict[str, Any], graph: Dict[str, Any], context: List[Dict]) -> Dict[str, Any]:
        """Add semantic enrichment to edge"""
        enrichment = {}

        # Classify semantic type of edge
        edge_type = edge['type']

        if edge_type == 'contains':
            enrichment['semantic_type'] = 'composition'
        elif edge_type == 'imports':
            enrichment['semantic_type'] = 'dependency'
        elif edge_type == 'inherits':
            enrichment['semantic_type'] = 'inheritance'
        elif edge_type == 'calls':
            enrichment['semantic_type'] = 'invocation'
        else:
            enrichment['semantic_type'] = 'unknown'

        return enrichment
