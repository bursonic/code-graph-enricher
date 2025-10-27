#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures
"""

import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict, Any


@pytest.fixture
def sample_graph() -> Dict[str, Any]:
    """Basic code graph fixture for testing"""
    return {
        "nodes": [
            {
                "id": "file1",
                "type": "file",
                "name": "user_service.py",
                "path": "src/services/user_service.py",
                "location": {"line": 1, "column": 0},
                "metadata": {
                    "imports": ["json", "typing", "models"]
                }
            },
            {
                "id": "class1",
                "type": "class",
                "name": "UserService",
                "path": "src/services/user_service.py",
                "location": {"line": 10, "column": 0},
                "metadata": {}
            },
            {
                "id": "func1",
                "type": "function",
                "name": "get_user",
                "path": "src/services/user_service.py",
                "location": {"line": 15, "column": 4},
                "metadata": {}
            },
            {
                "id": "func2",
                "type": "function",
                "name": "create_user",
                "path": "src/services/user_service.py",
                "location": {"line": 25, "column": 4},
                "metadata": {}
            },
            {
                "id": "func3",
                "type": "function",
                "name": "validate_email",
                "path": "src/services/user_service.py",
                "location": {"line": 35, "column": 4},
                "metadata": {}
            }
        ],
        "edges": [
            {
                "source": "file1",
                "target": "class1",
                "type": "contains"
            },
            {
                "source": "class1",
                "target": "func1",
                "type": "contains"
            },
            {
                "source": "class1",
                "target": "func2",
                "type": "contains"
            },
            {
                "source": "class1",
                "target": "func3",
                "type": "contains"
            },
            {
                "source": "func2",
                "target": "func3",
                "type": "calls"
            }
        ]
    }


@pytest.fixture
def entity_graph() -> Dict[str, Any]:
    """Graph with domain entities for testing domain enrichment"""
    return {
        "nodes": [
            {
                "id": "class_user",
                "type": "class",
                "name": "User",
                "path": "models/user.py",
                "location": {"line": 5, "column": 0},
                "metadata": {"is_dataclass": True}
            },
            {
                "id": "class_order",
                "type": "class",
                "name": "Order",
                "path": "models/order.py",
                "location": {"line": 10, "column": 0},
                "metadata": {}
            },
            {
                "id": "func_get_orders",
                "type": "function",
                "name": "get_orders",
                "path": "models/user.py",
                "location": {"line": 15, "column": 4},
                "metadata": {}
            },
            {
                "id": "func_calculate_total",
                "type": "function",
                "name": "calculate_total",
                "path": "models/order.py",
                "location": {"line": 20, "column": 4},
                "metadata": {}
            }
        ],
        "edges": [
            {
                "source": "class_user",
                "target": "func_get_orders",
                "type": "contains"
            },
            {
                "source": "class_order",
                "target": "func_calculate_total",
                "type": "contains"
            }
        ]
    }


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test output"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_source_dir():
    """Create a temporary directory with sample source files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create directory structure
        services_dir = tmppath / "src" / "services"
        services_dir.mkdir(parents=True, exist_ok=True)

        # Write sample source file
        user_service = services_dir / "user_service.py"
        user_service.write_text("""#!/usr/bin/env python3
import json
from typing import Optional

class UserService:
    \"\"\"Service for managing users\"\"\"

    def __init__(self):
        self.users = {}

    def get_user(self, user_id: str) -> Optional[dict]:
        \"\"\"Get a user by ID\"\"\"
        return self.users.get(user_id)

    def create_user(self, email: str, name: str) -> dict:
        \"\"\"Create a new user\"\"\"
        if not self.validate_email(email):
            raise ValueError("Invalid email")

        user = {"email": email, "name": name}
        self.users[email] = user
        return user

    def validate_email(self, email: str) -> bool:
        \"\"\"Validate email format\"\"\"
        return "@" in email
""")

        yield tmppath


@pytest.fixture
def enriched_graph_layer1(sample_graph) -> Dict[str, Any]:
    """Graph with Layer 1 enrichment already applied"""
    graph = json.loads(json.dumps(sample_graph))  # Deep copy

    for node in graph['nodes']:
        node['enrichment'] = {
            'layer1': {
                'classification': 'domain' if 'service' in node['name'].lower() else 'infrastructure',
                'complexity': {
                    'loc': 10,
                    'nesting_depth': 1,
                    'num_params': 2,
                    'num_methods': 3 if node['type'] == 'class' else 0
                },
                'dependencies': {
                    'import_depth': 1,
                    'num_imports': 3,
                    'imports_from': []
                }
            }
        }

    return graph


@pytest.fixture
def enriched_graph_layer2(enriched_graph_layer1) -> Dict[str, Any]:
    """Graph with Layer 1 and Layer 2 enrichment already applied"""
    graph = json.loads(json.dumps(enriched_graph_layer1))  # Deep copy

    for node in graph['nodes']:
        patterns = []
        if node['type'] == 'class' and 'service' in node['name'].lower():
            patterns = ['Service']
        elif node['type'] == 'class' and any(term in node['name'].lower() for term in ['user', 'order', 'product']):
            patterns = ['Entity']

        node['enrichment']['layer2'] = {
            'patterns': patterns,
            'naming_analysis': {
                'terms': node['name'].lower().split('_'),
                'conventions': 'snake_case' if '_' in node['name'] else 'PascalCase',
                'role_indicators': []
            },
            'method_roles': [],
            'api_surface': 'public'
        }

    # Add layer2 enrichment to edges as well
    for edge in graph['edges']:
        if 'enrichment' not in edge:
            edge['enrichment'] = {}
        edge['enrichment']['layer2'] = {
            'semantic_type': 'composition' if edge['type'] == 'contains' else 'unknown'
        }

    return graph
