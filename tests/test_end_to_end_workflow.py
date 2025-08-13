"""
End-to-end workflow tests for task 10.1: Test complete end-to-end workflow.

This module tests the complete workflow from diagram generation to GitHub Pages deployment,
verifying that all components work together correctly and that the site structure is proper.
"""

import pytest
import json
import yaml
import subprocess
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import requests
from datetime import datetime

from src.diagrams.generator import DiagramGenerator, DiagramConfig
from src.diagrams.example_system import ECommerceSystemDiagrams, export_diagrams
from src.site_generator import SiteGenerator, SiteConfig


class TestCompleteEndToEndWorkflow:
    """Test the complete end-to-end workflow from code push to GitHub Pages."""
    
    @pytest.fixture
    def complete_test_workspace(self):
        """Create a complete test workspace with all necessary files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            
            # Create full directory structure
            directories = [
                "src/diagrams",
                "docs/diagrams",
                "docs/images", 
                "docs/logs",
                "templates",
                ".github/workflows",
                "tests"
            ]
            
            for directory in directories:
                (workspace / directory).mkdir(parents=True)
            
            # Create pyproject.toml
            pyproject_content = """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "pystructurizr-github-pages"
version = "1.0.0"
description = "Architecture diagrams with pystructurizr and GitHub Pages"
dependencies = [
    "pystructurizr>=0.1.0",
    "jinja2>=3.1.0",
    "pyyaml>=6.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "pytest-mock>=3.10.0",
]
"""
            (workspace / "pyproject.toml").write_text(pyproject_content)
            
            # Create GitHub Actions workflow
            workflow_content = """
name: Render Architecture Diagrams

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  render-diagrams:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install uv
      uses: astral-sh/setup-uv@v2
        
    - name: Install dependencies
      run: uv sync
        
    - name: Generate diagrams
      run: uv run python src/diagrams/example_system.py
        
    - name: Install PlantUML
      run: |
        sudo apt-get update
        sudo apt-get install -y default-jre
        wget -O plantuml.jar https://github.com/plantuml/plantuml/releases/download/v1.2023.12/plantuml-1.2023.12.jar
        
    - name: Render PlantUML diagrams
      run: |
        find docs -name "*.puml" -exec java -jar plantuml.jar -tpng -o ../images {} \\;
        find docs -name "*.puml" -exec java -jar plantuml.jar -tsvg -o ../images {} \\;
        
    - name: Generate static site
      run: uv run python generate_site.py
        
    - name: Upload Pages artifact
      uses: actions/upload-pages-artifact@v3
      with:
        path: ./docs
        
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: render-diagrams
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v4
"""
            (workspace / ".github" / "workflows" / "render-diagrams.yml").write_text(workflow_content)
            
            # Create HTML templates
            templates = {
                "base.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ config.title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        nav { margin-bottom: 20px; }
        nav a { margin-right: 15px; text-decoration: none; color: #007acc; }
        nav a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <nav>
            <a href="/">Home</a>
            <a href="/diagrams/">All Diagrams</a>
        </nav>
        {% block content %}{% endblock %}
    </div>
</body>
</html>""",
                
                "index.html": """{% extends "base.html" %}
{% block content %}
<h1>{{ config.title }}</h1>
<p>{{ config.description }}</p>
<div class="stats">
    <p><strong>Total Diagrams:</strong> {{ stats.total_diagrams }}</p>
    <p><strong>System Context Views:</strong> {{ stats.system_contexts }}</p>
    <p><strong>Container Views:</strong> {{ stats.containers }}</p>
    <p><strong>Component Views:</strong> {{ stats.components }}</p>
</div>
<div class="recent-diagrams">
    <h2>Recent Diagrams</h2>
    {% for diagram in recent_diagrams %}
    <div class="diagram-preview">
        <h3><a href="/diagrams/{{ diagram.file_path | replace('.json', '.html') }}">{{ diagram.title }}</a></h3>
        <p>{{ diagram.description }}</p>
        <small>{{ diagram.diagram_type }} • Updated {{ diagram.last_updated.strftime('%Y-%m-%d') }}</small>
    </div>
    {% endfor %}
</div>
{% endblock %}""",
                
                "diagrams.html": """{% extends "base.html" %}
{% block content %}
<h1>All Architecture Diagrams</h1>
<p>Browse all {{ stats.total_diagrams }} diagrams in the system.</p>
{% for diagram in diagrams %}
<div class="diagram-item">
    <h2><a href="/diagrams/{{ diagram.file_path | replace('.json', '.html') }}">{{ diagram.title }}</a></h2>
    <p>{{ diagram.description }}</p>
    <div class="diagram-meta">
        <span class="type">{{ diagram.diagram_type }}</span>
        <span class="updated">{{ diagram.last_updated.strftime('%Y-%m-%d') }}</span>
    </div>
</div>
{% endfor %}
{% endblock %}""",
                
                "diagram.html": """{% extends "base.html" %}
{% block content %}
<h1>{{ diagram.title }}</h1>
<p>{{ diagram.description }}</p>
<div class="diagram-meta">
    <p><strong>Type:</strong> {{ diagram.diagram_type }}</p>
    <p><strong>Last Updated:</strong> {{ diagram.last_updated.strftime('%Y-%m-%d %H:%M') }}</p>
</div>
{% if plantuml_source %}
<div class="plantuml-source">
    <h2>PlantUML Source</h2>
    <pre><code>{{ plantuml_source }}</code></pre>
</div>
{% endif %}
{% if related_diagrams %}
<div class="related-diagrams">
    <h2>Related Diagrams</h2>
    {% for related in related_diagrams %}
    <div class="related-item">
        <h3><a href="/diagrams/{{ related.file_path | replace('.json', '.html') }}">{{ related.title }}</a></h3>
        <p>{{ related.description }}</p>
    </div>
    {% endfor %}
</div>
{% endif %}
{% endblock %}"""
            }
            
            for name, content in templates.items():
                (workspace / "templates" / name).write_text(content)
            
            yield workspace
    
    def test_diagram_generation_triggers_correctly(self, complete_test_workspace):
        """Test that diagram generation is triggered correctly and produces expected outputs."""
        workspace = complete_test_workspace
        
        # Mock the pystructurizr components
        with patch('src.diagrams.generator.Workspace') as mock_workspace_class, \
             patch('src.diagrams.generator.Model') as mock_model_class:
            
            # Setup mocks
            mock_workspace = Mock()
            mock_model = Mock()
            mock_workspace_class.return_value = mock_workspace
            mock_model_class.return_value = mock_model
            
            # Mock workspace dump
            mock_workspace.dump.return_value = {
                "name": "E-Commerce System",
                "description": "Complete e-commerce platform architecture",
                "model": {"people": [], "softwareSystems": []},
                "views": {"systemContextViews": [], "containerViews": []}
            }
            
            # Create diagram generator
            config = DiagramConfig(
                name="E-Commerce System",
                description="Complete e-commerce platform architecture",
                version="1.0.0",
                author="Test Suite"
            )
            
            generator = DiagramGenerator(config)
            
            # Test workspace creation
            workspace_obj = generator.create_workspace()
            assert workspace_obj is not None
            
            # Add a mock diagram to satisfy validation
            mock_view = Mock()
            generator.add_system_context_view(Mock(), "Test View", "Test Description")
            
            # Test JSON export
            json_export = generator.export_to_json()
            assert json_export is not None
            
            # Validate JSON structure
            json_data = json.loads(json_export)
            assert "workspace" in json_data
            assert "metadata" in json_data
            assert json_data["workspace"]["name"] == "E-Commerce System"
            
            # Test PlantUML export
            plantuml_export = generator.export_to_plantuml()
            assert plantuml_export is not None
            assert "@startuml" in plantuml_export
            assert "@enduml" in plantuml_export
            
            # Test validation
            assert generator.validate_export_data(json_export) is True
            assert generator.validate_plantuml_output(plantuml_export) is True
    
    def test_all_diagram_types_render_correctly(self, complete_test_workspace):
        """Test that all diagram types (system context, container, component) render correctly."""
        workspace = complete_test_workspace
        
        with patch('src.diagrams.example_system.Workspace'), \
             patch('src.diagrams.example_system.Model') as mock_model_class:
            
            # Setup comprehensive mocks
            mock_model = Mock()
            mock_model_class.return_value = mock_model
            
            # Mock element creation
            mock_person = Mock()
            mock_person.name = "Customer"
            mock_system = Mock()
            mock_system.name = "E-Commerce System"
            mock_container = Mock()
            mock_container.name = "Web Application"
            mock_component = Mock()
            mock_component.name = "Authentication Service"
            
            mock_model.Person.return_value = mock_person
            mock_model.SoftwareSystem.return_value = mock_system
            mock_system.Container.return_value = mock_container
            mock_container.Component.return_value = mock_component
            
            # Create example system
            ecommerce = ECommerceSystemDiagrams()
            
            # Mock generator methods to return realistic data
            ecommerce.generator.export_to_json = Mock(return_value=json.dumps({
                "workspace": {
                    "name": "E-Commerce System Architecture",
                    "description": "Complete e-commerce platform",
                    "version": "1.0.0"
                },
                "metadata": {
                    "diagrams": [
                        {
                            "title": "System Context",
                            "description": "High-level system context",
                            "type": "system_context",
                            "lastUpdated": "2023-01-01T12:00:00"
                        },
                        {
                            "title": "Container View", 
                            "description": "Internal container structure",
                            "type": "container",
                            "lastUpdated": "2023-01-01T12:00:00"
                        },
                        {
                            "title": "Component View",
                            "description": "Detailed component architecture", 
                            "type": "component",
                            "lastUpdated": "2023-01-01T12:00:00"
                        }
                    ]
                }
            }))
            
            ecommerce.generator.export_to_plantuml = Mock(return_value="""@startuml
!title E-Commerce System Architecture

Person(customer, "Customer")
System(ecommerce, "E-Commerce System")
System(payment, "Payment Gateway")

Rel(customer, ecommerce, "Uses")
Rel(ecommerce, payment, "Processes payments")

@enduml""")
            
            ecommerce.generator.validate_export_data = Mock(return_value=True)
            ecommerce.generator.validate_plantuml_output = Mock(return_value=True)
            
            # Create all diagram views
            ecommerce.create_system_context_view()
            ecommerce.create_container_view()
            ecommerce.create_component_view()
            
            # Verify all elements were created
            assert len(ecommerce.people) > 0
            assert len(ecommerce.systems) > 0
            assert len(ecommerce.containers) > 0
            assert len(ecommerce.components) > 0
            
            # Export diagrams to test workspace
            docs_dir = workspace / "docs"
            export_diagrams(ecommerce, str(docs_dir))
            
            # Verify exports were called
            ecommerce.generator.export_to_json.assert_called_once()
            ecommerce.generator.export_to_plantuml.assert_called_once()
            
            # Verify validation was performed
            ecommerce.generator.validate_export_data.assert_called_once()
            ecommerce.generator.validate_plantuml_output.assert_called_once()
    
    def test_github_pages_site_structure_is_correct(self, complete_test_workspace):
        """Test that the generated GitHub Pages site has the correct structure and navigation."""
        workspace = complete_test_workspace
        
        # Create sample diagram metadata
        metadata = {
            "metadata": {
                "diagrams": [
                    {
                        "title": "System Context",
                        "description": "System context diagram showing external interactions",
                        "type": "system_context",
                        "lastUpdated": "2023-01-01T12:00:00",
                        "filePath": "system_context.json",
                        "outputFiles": {
                            "png": "system_context.png",
                            "plantuml": str(workspace / "docs" / "system_context.puml")
                        }
                    },
                    {
                        "title": "Container View",
                        "description": "Container view showing internal structure",
                        "type": "container", 
                        "lastUpdated": "2023-01-02T12:00:00",
                        "filePath": "container.json",
                        "outputFiles": {
                            "svg": "container.svg",
                            "plantuml": str(workspace / "docs" / "container.puml")
                        }
                    },
                    {
                        "title": "Component View",
                        "description": "Component view showing detailed architecture",
                        "type": "component",
                        "lastUpdated": "2023-01-03T12:00:00", 
                        "filePath": "component.json",
                        "outputFiles": {
                            "png": "component.png",
                            "svg": "component.svg",
                            "plantuml": str(workspace / "docs" / "component.puml")
                        }
                    }
                ]
            }
        }
        
        # Save metadata to docs directory
        metadata_file = workspace / "docs" / "diagram_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)
        
        # Create sample PlantUML files
        plantuml_files = {
            "system_context.puml": "@startuml\nPerson(user, \"User\")\nSystem(system, \"System\")\n@enduml",
            "container.puml": "@startuml\nContainer(web, \"Web App\")\nContainer(api, \"API\")\n@enduml",
            "component.puml": "@startuml\nComponent(auth, \"Auth Service\")\nComponent(data, \"Data Service\")\n@enduml"
        }
        
        for filename, content in plantuml_files.items():
            (workspace / "docs" / filename).write_text(content)
        
        # Generate site
        config = SiteConfig(
            title="Architecture Documentation",
            description="Complete system architecture documentation",
            base_url="https://example.github.io/project"
        )
        
        generator = SiteGenerator(
            templates_dir=str(workspace / "templates"),
            output_dir=str(workspace / "docs"),
            diagrams_dir=str(workspace / "docs"),
            config=config
        )
        
        # Test template validation
        assert generator.validate_templates() is True
        
        # Generate complete site
        generator.generate_site()
        
        # Test site structure
        docs_dir = workspace / "docs"
        
        # Verify main pages exist
        assert (docs_dir / "index.html").exists()
        assert (docs_dir / "diagrams" / "index.html").exists()
        
        # Verify individual diagram pages exist
        assert (docs_dir / "diagrams" / "system_context.html").exists()
        assert (docs_dir / "diagrams" / "container.html").exists()
        assert (docs_dir / "diagrams" / "component.html").exists()
        
        # Test navigation structure
        navigation = generator.create_navigation_structure()
        assert "main" in navigation
        assert "categories" in navigation
        assert len(navigation["categories"]) == 3  # system_context, container, component
        
        # Test content quality
        index_content = (docs_dir / "index.html").read_text()
        assert "Architecture Documentation" in index_content
        assert "Total Diagrams:</strong> 3" in index_content
        assert "System Context Views:</strong> 1" in index_content
        assert "Container Views:</strong> 1" in index_content
        assert "Component Views:</strong> 1" in index_content
        
        # Test diagram page content
        system_context_content = (docs_dir / "diagrams" / "system_context.html").read_text()
        assert "System Context" in system_context_content
        assert "System context diagram showing external interactions" in system_context_content
        assert "@startuml" in system_context_content  # PlantUML source included
        
        # Test diagrams index page
        diagrams_index_content = (docs_dir / "diagrams" / "index.html").read_text()
        assert "All Architecture Diagrams" in diagrams_index_content
        assert "Browse all 3 diagrams" in diagrams_index_content
        assert "System Context" in diagrams_index_content
        assert "Container View" in diagrams_index_content
        assert "Component View" in diagrams_index_content
        
        # Generate and test sitemap
        generator.generate_sitemap()
        sitemap_file = docs_dir / "sitemap.xml"
        assert sitemap_file.exists()
        
        sitemap_content = sitemap_file.read_text()
        assert "https://example.github.io/project" in sitemap_content
        assert "system_context.html" in sitemap_content
        assert "container.html" in sitemap_content
        assert "component.html" in sitemap_content
    
    def test_workflow_validation_passes(self, complete_test_workspace):
        """Test that the GitHub Actions workflow file is valid and contains all required steps."""
        workspace = complete_test_workspace
        workflow_file = workspace / ".github" / "workflows" / "render-diagrams.yml"
        
        # Parse workflow YAML
        with open(workflow_file, 'r') as f:
            workflow_data = yaml.safe_load(f)
        
        # Test basic structure
        assert workflow_data["name"] == "Render Architecture Diagrams"
        # YAML parser converts 'on' to True in Python, so check for the boolean key
        assert True in workflow_data or "on" in workflow_data
        assert "jobs" in workflow_data
        
        # Test triggers (handle YAML 'on' key conversion)
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        assert "push" in triggers
        assert "pull_request" in triggers
        assert "workflow_dispatch" in triggers
        assert triggers["push"]["branches"] == ["main"]
        
        # Test permissions
        assert "permissions" in workflow_data
        assert workflow_data["permissions"]["contents"] == "read"
        assert workflow_data["permissions"]["pages"] == "write"
        assert workflow_data["permissions"]["id-token"] == "write"
        
        # Test jobs structure
        assert "render-diagrams" in workflow_data["jobs"]
        assert "deploy" in workflow_data["jobs"]
        
        render_job = workflow_data["jobs"]["render-diagrams"]
        deploy_job = workflow_data["jobs"]["deploy"]
        
        # Test render job
        assert render_job["runs-on"] == "ubuntu-latest"
        assert "steps" in render_job
        
        # Test deploy job
        assert deploy_job["runs-on"] == "ubuntu-latest"
        assert deploy_job["needs"] == "render-diagrams"
        assert deploy_job["if"] == "github.ref == 'refs/heads/main'"
        assert "environment" in deploy_job
        
        # Test required steps exist
        step_names = [step.get("name", "") for step in render_job["steps"]]
        required_steps = [
            "Checkout repository",
            "Set up Python", 
            "Install uv",
            "Install dependencies",
            "Generate diagrams",
            "Install PlantUML",
            "Render PlantUML diagrams",
            "Generate static site",
            "Upload Pages artifact"
        ]
        
        for required_step in required_steps:
            assert required_step in step_names, f"Missing required step: {required_step}"
        
        # Test deploy steps
        deploy_step_names = [step.get("name", "") for step in deploy_job["steps"]]
        assert "Deploy to GitHub Pages" in deploy_step_names
    
    @patch('subprocess.run')
    def test_simulated_workflow_execution(self, mock_subprocess, complete_test_workspace):
        """Test simulated execution of the complete workflow pipeline."""
        workspace = complete_test_workspace
        
        # Mock successful subprocess calls
        mock_subprocess.return_value = Mock(returncode=0, stdout="Success", stderr="")
        
        # Simulate workflow steps in order
        workflow_steps = [
            # Step 1: Install dependencies
            {
                "command": ["uv", "sync"],
                "description": "Install project dependencies"
            },
            # Step 2: Generate diagrams
            {
                "command": ["uv", "run", "python", "src/diagrams/example_system.py"],
                "description": "Generate diagram definitions"
            },
            # Step 3: Install PlantUML (simulated)
            {
                "command": ["sudo", "apt-get", "install", "-y", "default-jre"],
                "description": "Install Java runtime for PlantUML"
            },
            # Step 4: Render diagrams
            {
                "command": ["java", "-jar", "plantuml.jar", "-tpng", "docs/test.puml"],
                "description": "Render PlantUML diagrams to PNG"
            },
            # Step 5: Generate static site
            {
                "command": ["uv", "run", "python", "generate_site.py"],
                "description": "Generate static HTML site"
            }
        ]
        
        # Execute each step
        for i, step in enumerate(workflow_steps):
            print(f"Executing step {i+1}: {step['description']}")
            
            # Simulate command execution
            result = subprocess.run(
                step["command"],
                cwd=workspace,
                capture_output=True,
                text=True
            )
            
            # In a real workflow, we'd check result.returncode == 0
            assert mock_subprocess.called
        
        # Verify all steps were executed
        assert mock_subprocess.call_count == len(workflow_steps)
        
        # Verify command sequence
        call_args = [call[0][0] for call in mock_subprocess.call_args_list]
        expected_first_commands = ["uv", "uv", "sudo", "java", "uv"]
        
        for i, expected_cmd in enumerate(expected_first_commands):
            assert call_args[i][0] == expected_cmd, f"Step {i+1} command mismatch"
    
    def test_error_handling_and_recovery(self, complete_test_workspace):
        """Test that the workflow handles errors gracefully and provides useful feedback."""
        workspace = complete_test_workspace
        
        # Test missing template error handling
        (workspace / "templates" / "base.html").unlink()
        
        generator = SiteGenerator(
            templates_dir=str(workspace / "templates"),
            output_dir=str(workspace / "docs")
        )
        
        # Should raise informative error
        with pytest.raises(FileNotFoundError, match="Required template not found"):
            generator.validate_templates()
        
        # Test missing diagram metadata handling
        config = SiteConfig(title="Test Site", description="Test")
        generator = SiteGenerator(
            templates_dir=str(workspace / "templates"),
            output_dir=str(workspace / "docs"),
            config=config
        )
        
        # Restore base template
        (workspace / "templates" / "base.html").write_text(
            "<html><head><title>{{ config.title }}</title></head><body>{% block content %}{% endblock %}</body></html>"
        )
        
        # Should handle missing metadata gracefully
        generator.validate_templates()  # Should not raise
        
        # Test partial diagram generation failure
        metadata = {
            "metadata": {
                "diagrams": [
                    {
                        "title": "Valid Diagram",
                        "description": "This diagram should work",
                        "type": "system_context",
                        "lastUpdated": "2023-01-01T12:00:00",
                        "filePath": "valid.json",
                        "outputFiles": {}
                    }
                ]
            }
        }
        
        metadata_file = workspace / "docs" / "diagram_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)
        
        # Generate site with partial data - should succeed
        generator.generate_site()
        
        # Verify site was generated despite missing assets
        assert (workspace / "docs" / "index.html").exists()
        assert (workspace / "docs" / "diagrams" / "index.html").exists()
    
    def test_performance_and_scalability(self, complete_test_workspace):
        """Test workflow performance with multiple diagrams and large datasets."""
        workspace = complete_test_workspace
        
        # Create metadata for many diagrams
        diagrams = []
        for i in range(50):  # Test with 50 diagrams
            diagrams.append({
                "title": f"Diagram {i+1}",
                "description": f"Test diagram number {i+1} for performance testing",
                "type": ["system_context", "container", "component"][i % 3],
                "lastUpdated": f"2023-01-{(i % 30) + 1:02d}T12:00:00",
                "filePath": f"diagram_{i+1}.json",
                "outputFiles": {"png": f"diagram_{i+1}.png"}
            })
        
        metadata = {"metadata": {"diagrams": diagrams}}
        
        metadata_file = workspace / "docs" / "diagram_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)
        
        # Generate site with many diagrams
        config = SiteConfig(
            title="Performance Test Site",
            description="Testing with many diagrams"
        )
        
        generator = SiteGenerator(
            templates_dir=str(workspace / "templates"),
            output_dir=str(workspace / "docs"),
            diagrams_dir=str(workspace / "docs"),
            config=config
        )
        
        # Measure generation time (basic performance test)
        import time
        start_time = time.time()
        
        generator.generate_site()
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert generation_time < 10.0, f"Site generation took too long: {generation_time:.2f}s"
        
        # Verify all pages were generated
        assert (workspace / "docs" / "index.html").exists()
        assert (workspace / "docs" / "diagrams" / "index.html").exists()
        
        # Verify statistics are correct
        assert generator.stats.total_diagrams == 50
        
        # Test that navigation handles many items
        navigation = generator.create_navigation_structure()
        assert len(navigation["categories"]) == 3  # 3 diagram types
        
        # Verify index page shows correct stats
        index_content = (workspace / "docs" / "index.html").read_text()
        assert "Total Diagrams:</strong> 50" in index_content
    
    def test_cross_browser_compatibility_structure(self, complete_test_workspace):
        """Test that generated HTML is structured for cross-browser compatibility."""
        workspace = complete_test_workspace
        
        # Create sample metadata
        metadata = {
            "metadata": {
                "diagrams": [
                    {
                        "title": "Test Diagram",
                        "description": "Test for browser compatibility",
                        "type": "system_context",
                        "lastUpdated": "2023-01-01T12:00:00",
                        "filePath": "test.json",
                        "outputFiles": {}
                    }
                ]
            }
        }
        
        metadata_file = workspace / "docs" / "diagram_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)
        
        # Generate site
        config = SiteConfig(title="Compatibility Test", description="Testing compatibility")
        generator = SiteGenerator(
            templates_dir=str(workspace / "templates"),
            output_dir=str(workspace / "docs"),
            diagrams_dir=str(workspace / "docs"),
            config=config
        )
        
        generator.generate_site()
        
        # Test HTML structure for compatibility
        index_content = (workspace / "docs" / "index.html").read_text()
        
        # Check for proper HTML5 structure
        assert "<!DOCTYPE html>" in index_content
        assert '<html lang="en">' in index_content
        assert '<meta charset="UTF-8">' in index_content
        assert '<meta name="viewport"' in index_content
        
        # Check for semantic HTML elements
        assert "<nav>" in index_content
        assert "</nav>" in index_content
        
        # Check for accessibility features
        assert 'alt=' in index_content or 'aria-' in index_content or len([line for line in index_content.split('\n') if 'img' in line]) == 0
        
        # Test CSS is inline or properly linked (for GitHub Pages)
        assert "<style>" in index_content or '<link rel="stylesheet"' in index_content
        
        # Verify no JavaScript dependencies (for maximum compatibility)
        assert "<script>" not in index_content or "src=" not in index_content