# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-27

### Added
- Initial release of Code Graph Enricher
- Layer 1: Structural enrichment (classification, complexity, dependencies)
- Layer 2: Semantic enrichment (patterns, naming analysis, method roles)
- Layer 3: Domain enrichment (concepts, business rules, workflows, relationships)
- Iterative refinement with convergence detection
- Intermediate artifact preservation
- Index generation for fast lookups
- CLI tool with `enrich-graph` command
- Comprehensive documentation and examples
- Test data with Python e-commerce example

### Features
- Multi-layer enrichment pipeline
- Iterative processing with context passing
- Automatic convergence detection
- Entity, Service, Repository, Factory pattern detection
- Method role classification (getter, setter, validator, calculator, etc.)
- Entity relationship inference (HAS_MANY, HAS_ONE, USES)
- Domain concept extraction
- Business rule identification
- Workflow detection

### Supported Patterns
- Entity
- ValueObject
- Service
- Repository
- Factory
- DTO

### Supported Languages
- Python (initial implementation)
- Extensible architecture for other languages

[0.1.0]: https://github.com/yourusername/code-graph-enricher/releases/tag/v0.1.0
