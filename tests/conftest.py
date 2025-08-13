"""
Pytest configuration and shared fixtures for the test suite.

This module provides common fixtures and configuration for all tests,
including test data, mock objects, and utility functions.
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock
from datetime import datetime

from src.diagrams.generator import DiagramConfig, DiagramMetadata
from src.site_generator import SiteConfig


@pytest.fixture
def sample_diagram_config():
    """Create a sample DiagramConfig for testing."""
    return DiagramConfig(
        name="Test System",
        description="A test system for unit testing",
        version="1.0.0",
        author="Test Suite",
        output_formats=["json", "plantuml"]
    )


@pytest.fixture
def sample_site_config():
    """Create a sample SiteConfig for testing."""
    return SiteConfig(
        title="Test Site",
        description="A test site for unit testing",
        base_url="https://test.example.com",
        theme="default"
    )


@pytest.fixture
def sample_diagram_metadata():
    """Create sample DiagramMetadata for testing."""
    return [
        DiagramMetadata(
            title="System Context",
            description="System context diagram showing external interactions",
            diagram_type="system_context",
            last_updated=datetime(2023, 1, 1, 12, 0, 0),
            file_path="system_context.json",
            output_files={"png": "system_context.png", "plantuml": "system_context.puml"}
        ),
        DiagramMetadata(
            title="Container View",
            description="Container view showing internal structure",
            diagram_type="container",
            last_updated=datetime(2023, 1, 2, 12, 0, 0),
            file_path="container.json",
            output_files={"png": "container.png", "svg": "container.svg"}
        ),
        DiagramMetadata(
            title="Component View",
            description="Component view showing detailed architecture",
            diagram_type="component",
            last_updated=datetime(2023, 1, 3, 12, 0, 0),
            file_path="component.json",
            output_files={}
        )
    ]


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory for testing."""
    with TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)
        
        # Create standard directory structure
        (workspace / "src" / "diagrams").mkdir(parents=True)
        (workspace / "docs").mkdir()
        (workspace / "templates").mkdir()
        (workspace / ".github" / "workflows").mkdir(parents=True)
        (workspace / "tests").mkdir()
        
        yield workspace


@pytest.fixture
def mock_pystructurizr_workspace():
    """Create a mock pystructurizr Workspace for testing."""
    mock_workspace = Mock()
    mock_workspace.dump.return_value = {
        "name": "Test Workspace",
        "description": "Test workspace description",
        "model": {
            "people": [],
            "softwareSystems": [],
            "relationships": []
        },
        "views": {
            "systemContextViews": [],
            "containerViews": [],
            "componentViews": []
        }
    }
    
    # Mock view creation methods
    mock_view = Mock()
    mock_workspace.SystemContextView.return_value = mock_view
    mock_workspace.ContainerView.return_value = mock_view
    mock_workspace.ComponentView.return_value = mock_view
    
    return mock_workspace


@pytest.fixture
def mock_pystructurizr_elements():
    """Create mock pystructurizr elements for testing."""
    mock_person = Mock()
    mock_person.name = "Test Person"
    mock_person.uses = Mock()
    
    mock_system = Mock()
    mock_system.name = "Test System"
    mock_system.uses = Mock()
    mock_system.Container = Mock()
    
    mock_container = Mock()
    mock_container.name = "Test Container"
    mock_container.uses = Mock()
    mock_container.Component = Mock()
    
    mock_component = Mock()
    mock_component.name = "Test Component"
    mock_component.uses = Mock()
    
    # Set up container and component creation
    mock_system.Container.return_value = mock_container
    mock_container.Component.return_value = mock_component
    
    return {
        "person": mock_person,
        "system": mock_system,
        "container": mock_container,
        "component": mock_component
    }


@pytest.fixture
def sample_json_export():
    """Create a sample JSON export for testing."""
    return {
        "workspace": {
            "name": "Test System",
            "description": "Test system description",
            "version": "1.0.0",
            "author": "Test Author",
            "lastUpdated": "2023-01-01T12:00:00",
            "configuration": {
                "outputFormats": ["json", "plantuml"]
            }
        },
        "model": {
            "people": [],
            "softwareSystems": [],
            "containers": [],
            "components": [],
            "relationships": []
        },
        "views": {
            "systemContextViews": [],
            "containerViews": [],
            "componentViews": [],
            "styles": {}
        },
        "metadata": {
            "diagrams": [
                {
                    "title": "Test Diagram",
                    "description": "Test description",
                    "type": "system_context",
                    "lastUpdated": "2023-01-01T12:00:00",
                    "filePath": "test.json",
                    "outputFiles": {}
                }
            ],
            "generatedAt": "2023-01-01T12:00:00",
            "generator": {
                "name": "pystructurizr-github-pages",
                "version": "1.0.0"
            }
        },
        "rawWorkspace": {}
    }


@pytest.fixture
def sample_plantuml_export():
    """Create a sample PlantUML export for testing."""
    return """@startuml
!title Test System

' Generated from pystructurizr workspace
' Author: Test Author
' Version: 1.0.0
' Generated at: 2023-01-01T12:00:00

' Include C4 model macros for better styling
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

' System Context View
Person(customer, "Customer", "A customer who uses the system")
System(system, "Test System", "The main system being documented")

' Relationships
Rel(customer, system, "Uses")

@enduml"""


@pytest.fixture
def sample_html_templates():
    """Create sample HTML templates for testing."""
    return {
        "base.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ config.title }}</title>
</head>
<body>
    <header>
        <h1>{{ config.title }}</h1>
        <nav>
            {% for item in config.navigation %}
            <a href="{{ item.url }}">{{ item.name }}</a>
            {% endfor %}
        </nav>
    </header>
    <main>
        {% block content %}{% endblock %}
    </main>
    <footer>
        <p>&copy; {{ current_year }} {{ config.title }}</p>
    </footer>
</body>
</html>""",
        
        "index.html": """{% extends "base.html" %}
{% block content %}
<section class="hero">
    <h2>{{ config.description }}</h2>
    <p>Total diagrams: {{ stats.total_diagrams }}</p>
</section>

<section class="recent-diagrams">
    <h3>Recent Diagrams</h3>
    {% for diagram in recent_diagrams %}
    <div class="diagram-card">
        <h4>{{ diagram.title }}</h4>
        <p>{{ diagram.description }}</p>
        <p>Type: {{ diagram.diagram_type }}</p>
        <p>Updated: {{ diagram.last_updated.strftime('%Y-%m-%d') }}</p>
    </div>
    {% endfor %}
</section>
{% endblock %}""",
        
        "diagrams.html": """{% extends "base.html" %}
{% block content %}
<section class="diagrams-list">
    <h2>All Diagrams</h2>
    <p>Total: {{ stats.total_diagrams }} diagrams</p>
    
    {% for diagram in diagrams %}
    <article class="diagram-item">
        <h3><a href="/diagrams/{{ diagram.file_path | replace('.json', '.html') }}">{{ diagram.title }}</a></h3>
        <p>{{ diagram.description }}</p>
        <div class="diagram-meta">
            <span class="type">{{ diagram.diagram_type }}</span>
            <span class="updated">{{ diagram.last_updated.strftime('%Y-%m-%d') }}</span>
        </div>
    </article>
    {% endfor %}
</section>
{% endblock %}""",
        
        "diagram.html": """{% extends "base.html" %}
{% block content %}
<article class="diagram-detail">
    <header>
        <h2>{{ diagram.title }}</h2>
        <p>{{ diagram.description }}</p>
        <div class="diagram-meta">
            <span class="type">Type: {{ diagram.diagram_type }}</span>
            <span class="updated">Last updated: {{ diagram.last_updated.strftime('%Y-%m-%d %H:%M') }}</span>
        </div>
    </header>
    
    {% if plantuml_source %}
    <section class="plantuml-source">
        <h3>PlantUML Source</h3>
        <pre><code>{{ plantuml_source }}</code></pre>
    </section>
    {% endif %}
    
    {% if related_diagrams %}
    <section class="related-diagrams">
        <h3>Related Diagrams</h3>
        {% for related in related_diagrams %}
        <div class="related-item">
            <h4><a href="/diagrams/{{ related.file_path | replace('.json', '.html') }}">{{ related.title }}</a></h4>
            <p>{{ related.description[:100] }}{% if related.description|length > 100 %}...{% endif %}</p>
        </div>
        {% endfor %}
    </section>
    {% endif %}
</article>
{% endblock %}"""
    }


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "workflow: GitHub Actions workflow tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file names
        if "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif any(name in item.nodeid for name in ["test_diagram_generator", "test_utils", "test_site_generator", "test_example_system"]):
            item.add_marker(pytest.mark.unit)
        
        # Add slow marker for integration tests
        if "integration" in item.keywords:
            item.add_marker(pytest.mark.slow)
        
        # Add workflow marker for GitHub Actions tests
        if "workflow" in item.name.lower() or "github" in item.name.lower():
            item.add_marker(pytest.mark.workflow)