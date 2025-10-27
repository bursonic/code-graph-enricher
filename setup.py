#!/usr/bin/env python3
"""
Setup script for Code Graph Enricher
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="code-graph-enricher",
    version="0.1.0",
    description="Iterative enrichment of code graphs with structural, semantic, and domain knowledge",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/code-graph-enricher",
    license="MIT",

    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},

    # Python version requirement
    python_requires=">=3.8",

    # Dependencies
    install_requires=[
        # No external dependencies - uses stdlib only
    ],

    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },

    # CLI entry point
    entry_points={
        "console_scripts": [
            "enrich-graph=enricher.cli:main",
        ],
    },

    # Package metadata
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],

    keywords="code-analysis ast graph enrichment domain-knowledge",

    project_urls={
        "Bug Reports": "https://github.com/yourusername/code-graph-enricher/issues",
        "Source": "https://github.com/yourusername/code-graph-enricher",
    },
)
