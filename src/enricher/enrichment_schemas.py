#!/usr/bin/env python3
"""
Schema definitions for enrichment layers
Each layer adds specific metadata to nodes/edges
"""

# Layer 1: Structural Enrichment
LAYER1_NODE_SCHEMA = {
    "classification": str,  # "domain", "infrastructure", "mixed", "unknown"
    "complexity": {
        "loc": int,  # lines of code
        "nesting_depth": int,
        "num_params": int,  # for functions
        "num_methods": int,  # for classes
    },
    "dependencies": {
        "import_depth": int,  # how deep in dependency chain
        "num_imports": int,
        "imports_from": list,  # list of module names
    }
}

# Layer 2: Semantic Enrichment
LAYER2_NODE_SCHEMA = {
    "patterns": list,  # ["Entity", "Service", "Repository", "Factory", "ValueObject"]
    "naming_analysis": {
        "terms": list,  # extracted domain terms from name
        "conventions": str,  # "snake_case", "camelCase", "PascalCase"
        "role_indicators": list,  # ["get", "set", "calculate", "validate"]
    },
    "method_roles": list,  # for functions: ["getter", "setter", "validator", "calculator", "transformer"]
    "api_surface": str,  # "public", "private", "protected"
}

# Layer 3: Domain Enrichment
LAYER3_NODE_SCHEMA = {
    "domain_concepts": list,  # ["User", "Order", "Product"] - extracted entities
    "business_rules": list,  # identified business rule candidates
    "workflow_participation": list,  # workflows this node participates in
    "entity_relationships": list,  # inferred relationships with other entities
}

# Layer 4: Cross-Reference Enrichment
LAYER4_NODE_SCHEMA = {
    "validated_relationships": list,  # relationships verified through multiple signals
    "concept_clusters": list,  # groups of related domain concepts
    "confidence_scores": dict,  # confidence in various inferences
}

# Edge enrichment schemas
EDGE_ENRICHMENT_SCHEMA = {
    "layer1": {
        "weight": float,  # importance/frequency
        "depth": int,  # distance from entry point
    },
    "layer2": {
        "semantic_type": str,  # "composition", "aggregation", "dependency", "inheritance"
    },
    "layer3": {
        "domain_relationship": str,  # "HAS_MANY", "BELONGS_TO", "USES", "CREATES"
    }
}
