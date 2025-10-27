"""
Code Graph Enricher

A tool for iterative enrichment of code graphs with structural, semantic, and domain knowledge.
"""

__version__ = "0.1.0"

from .iterative_enricher import IterativeEnricher, EnricherPass
from .layer1_structural import StructuralEnricher
from .layer2_semantic import SemanticEnricher
from .layer3_domain import DomainEnricher

__all__ = [
    "IterativeEnricher",
    "EnricherPass",
    "StructuralEnricher",
    "SemanticEnricher",
    "DomainEnricher",
]
