#!/usr/bin/env python3
"""
Layer 3: Domain Enrichment
Extracts domain concepts, business rules, and workflows
"""

from typing import Dict, List, Any, Set
from iterative_enricher import EnricherPass


class DomainEnricher(EnricherPass):
    """Layer 3: Domain knowledge extraction"""

    def __init__(self):
        super().__init__(layer_num=3, name="domain")

    def _extract_domain_concepts(self, node: Dict[str, Any], graph: Dict[str, Any], context: List[Dict]) -> List[str]:
        """Extract domain concept names from node"""
        concepts = []

        # Get previous layer enrichments
        layer2 = node.get('enrichment', {}).get('layer2', {})
        patterns = layer2.get('patterns', [])

        # If node is an Entity, it represents a domain concept
        if 'Entity' in patterns or 'ValueObject' in patterns:
            concepts.append(node['name'])

        # Extract from naming terms
        naming = layer2.get('naming_analysis', {})
        terms = naming.get('terms', [])

        # Known domain terms
        domain_keywords = [
            'user', 'customer', 'account', 'profile',
            'product', 'item', 'catalog', 'inventory',
            'order', 'purchase', 'transaction', 'sale',
            'cart', 'basket', 'checkout',
            'payment', 'invoice', 'receipt', 'billing',
            'shipping', 'delivery', 'address',
            'price', 'discount', 'coupon', 'promotion'
        ]

        for term in terms:
            if term in domain_keywords:
                concepts.append(term.capitalize())

        return list(set(concepts))  # Remove duplicates

    def _identify_business_rules(self, node: Dict[str, Any], graph: Dict[str, Any], context: List[Dict]) -> List[Dict[str, Any]]:
        """Identify potential business rules in the node"""
        rules = []

        if node['type'] != 'function':
            return rules

        # Get previous enrichments
        layer2 = node.get('enrichment', {}).get('layer2', {})
        method_roles = layer2.get('method_roles', [])
        naming = layer2.get('naming_analysis', {})

        # Validators often contain business rules
        if 'validator' in method_roles:
            rules.append({
                'type': 'validation',
                'description': f"Validation rule in {node['name']}",
                'location': f"{node['path']}:{node['location']['line']}"
            })

        # Calculators contain business logic
        if 'calculator' in method_roles:
            rules.append({
                'type': 'calculation',
                'description': f"Business calculation in {node['name']}",
                'location': f"{node['path']}:{node['location']['line']}"
            })

        # Functions with "apply", "check", "verify" suggest business rules
        name_lower = node['name'].lower()
        if any(keyword in name_lower for keyword in ['apply', 'check', 'verify', 'enforce', 'validate']):
            rules.append({
                'type': 'constraint',
                'description': f"Business constraint in {node['name']}",
                'location': f"{node['path']}:{node['location']['line']}"
            })

        return rules

    def _detect_workflow_participation(self, node: Dict[str, Any], graph: Dict[str, Any], context: List[Dict]) -> List[str]:
        """Detect which workflows this node participates in"""
        workflows = []

        if node['type'] != 'function':
            return workflows

        name = node['name'].lower()

        # Common workflow names based on function names
        workflow_patterns = {
            'authentication': ['login', 'logout', 'authenticate', 'verify', 'token'],
            'registration': ['register', 'signup', 'create_account'],
            'checkout': ['checkout', 'purchase', 'buy', 'place_order'],
            'cart_management': ['add_to_cart', 'remove_from_cart', 'update_cart', 'clear_cart'],
            'payment': ['pay', 'charge', 'process_payment', 'refund'],
            'order_fulfillment': ['ship', 'deliver', 'fulfill', 'track'],
            'user_management': ['create_user', 'update_user', 'delete_user', 'get_user'],
            'product_management': ['create_product', 'update_product', 'delete_product']
        }

        for workflow_name, keywords in workflow_patterns.items():
            if any(keyword in name for keyword in keywords):
                workflows.append(workflow_name)

        return workflows

    def _infer_entity_relationships(self, node: Dict[str, Any], graph: Dict[str, Any], context: List[Dict]) -> List[Dict[str, str]]:
        """Infer relationships between entities based on node structure"""
        relationships = []

        # Only process classes that are entities
        layer2 = node.get('enrichment', {}).get('layer2', {})
        patterns = layer2.get('patterns', [])

        if node['type'] != 'class' or 'Entity' not in patterns:
            return relationships

        # Look at methods to infer relationships
        for edge in graph['edges']:
            if edge['source'] == node['id'] and edge['type'] == 'contains':
                # Find the target node (method)
                target_node = next((n for n in graph['nodes'] if n['id'] == edge['target']), None)
                if not target_node or target_node['type'] != 'function':
                    continue

                method_name = target_node['name'].lower()

                # Infer HAS_MANY relationship
                if method_name.startswith('get_') and (method_name.endswith('s') or 'list' in method_name):
                    # e.g., get_orders() suggests User HAS_MANY Order
                    related_entity = method_name.replace('get_', '').replace('_list', '').strip('s')
                    relationships.append({
                        'type': 'HAS_MANY',
                        'target': related_entity.capitalize(),
                        'inferred_from': f"{node['name']}.{target_node['name']}"
                    })

                # Infer HAS_ONE/BELONGS_TO
                if method_name.startswith('get_') and not method_name.endswith('s'):
                    related_entity = method_name.replace('get_', '')
                    relationships.append({
                        'type': 'HAS_ONE',
                        'target': related_entity.capitalize(),
                        'inferred_from': f"{node['name']}.{target_node['name']}"
                    })

                # Infer USES relationship from "add" or "use" methods
                if any(verb in method_name for verb in ['add_', 'use_', 'apply_']):
                    for verb in ['add_', 'use_', 'apply_']:
                        if verb in method_name:
                            related_entity = method_name.replace(verb, '')
                            relationships.append({
                                'type': 'USES',
                                'target': related_entity.capitalize(),
                                'inferred_from': f"{node['name']}.{target_node['name']}"
                            })
                            break

        return relationships

    def enrich_node(self, node: Dict[str, Any], graph: Dict[str, Any], context: List[Dict]) -> Dict[str, Any]:
        """Add domain enrichment to node"""
        enrichment = {}

        # Extract domain concepts
        enrichment['domain_concepts'] = self._extract_domain_concepts(node, graph, context)

        # Identify business rules
        enrichment['business_rules'] = self._identify_business_rules(node, graph, context)

        # Detect workflow participation
        enrichment['workflow_participation'] = self._detect_workflow_participation(node, graph, context)

        # Infer entity relationships
        enrichment['entity_relationships'] = self._infer_entity_relationships(node, graph, context)

        return enrichment

    def enrich_edge(self, edge: Dict[str, Any], graph: Dict[str, Any], context: List[Dict]) -> Dict[str, Any]:
        """Add domain enrichment to edge"""
        enrichment = {}

        # Try to classify domain relationship type
        source_node = next((n for n in graph['nodes'] if n['id'] == edge['source']), None)
        target_node = next((n for n in graph['nodes'] if n['id'] == edge['target']), None)

        if not source_node or not target_node:
            return enrichment

        # Get patterns from both nodes
        source_patterns = source_node.get('enrichment', {}).get('layer2', {}).get('patterns', [])
        target_patterns = target_node.get('enrichment', {}).get('layer2', {}).get('patterns', [])

        # Classify relationship based on patterns and edge type
        if edge['type'] == 'contains':
            if 'Entity' in source_patterns:
                enrichment['domain_relationship'] = 'DEFINES'
        elif edge['type'] == 'imports':
            if 'Entity' in source_patterns and 'Entity' in target_patterns:
                enrichment['domain_relationship'] = 'DEPENDS_ON'
            elif 'Service' in source_patterns:
                enrichment['domain_relationship'] = 'USES'
        elif edge['type'] == 'calls':
            enrichment['domain_relationship'] = 'INVOKES'

        return enrichment
