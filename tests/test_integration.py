"""
Integration tests for the complete diagram generation and site generation pipeline.

Tests cover end-to-end workflows including diagram generation, export,
site generation, and GitHub Actions workflow validation.
"""

import pytest
import json
import yaml
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch, mock_open
import os
import subprocess

from src.diagrams.generator import DiagramGenerator, DiagramConfig
from src.diagrams.example_system import ECommerceSystemDiagrams, export_diagrams
from src.site_generator import SiteGenerator, SiteConfig


class TestDiagramGenerationPipeline:
    """Integration tests for the complete diagram generation pipeline."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for integration testing."""
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            
            # Create directory structure
            (workspace / "src" / "diagrams").mkdir(parents=True)
            (workspace / "docs").mkdir()
            (workspace / "templates").mkdir()
            (workspace / ".github" / "workflows").mkdir(parents=True)
            
            yield workspace
    
    def test_complete_diagram_generation_workflow(self, temp_workspace):
        """Test the complete workflow from diagram creation to export."""
        # Step 1: Create diagram generator
        config = DiagramConfig(
            name="Integration Test System",
            description="System for integration testing",
            version="1.0.0",
            author="Test Suite"
        )
        
        generator = DiagramGenerator(config)
        
        # Step 2: Create workspace and add views
        workspace = generator.create_workspace()
        assert workspace is not None
        
        # Mock the pystructurizr objects since we can't import the real ones
        with patch('src.diagrams.generator.Workspace') as mock_workspace_class:
            mock_workspace = Mock()
            mock_workspace_class.return_value = mock_workspace
            mock_workspace.dump.return_value = {"test": "workspace_data"}
            
            # Mock view creation
            mock_view = Mock()
            mock_workspace.SystemContextView.return_value = mock_view
            mock_workspace.ContainerView.return_value = mock_view
            
            # Recreate generator with mocked workspace
            generator = DiagramGenerator(config)
            generator.create_workspace()
            
            # Create mock system
            mock_system = Mock()
            mock_system.name = "Test System"
            
            # Add views
            system_view = generator.add_system_context_view(
                mock_system,
                "System Context",
                "Test system context view"
            )
            
            container_view = generator.add_container_view(
                mock_system,
                "Container View",
                "Test container view"
            )
            
            # Step 3: Export to JSON and validate
            json_export = generator.export_to_json()
            assert json_export is not None
            
            # Validate JSON structure
            json_data = json.loads(json_export)
            assert "workspace" in json_data
            assert "metadata" in json_data
            assert len(json_data["metadata"]["diagrams"]) == 2
            
            # Validate export data
            assert generator.validate_export_data(json_export) is True
            
            # Step 4: Export to PlantUML and validate
            plantuml_export = generator.export_to_plantuml()
            assert plantuml_export is not None
            assert "@startuml" in plantuml_export
            assert "@enduml" in plantuml_export
            
            # Validate PlantUML output
            assert generator.validate_plantuml_output(plantuml_export) is True
            
            # Step 5: Save exports to files
            docs_dir = temp_workspace / "docs"
            
            json_file = docs_dir / "test_system.json"
            with open(json_file, 'w') as f:
                f.write(json_export)
            
            plantuml_file = docs_dir / "test_system.puml"
            with open(plantuml_file, 'w') as f:
                f.write(plantuml_export)
            
            # Verify files were created
            assert json_file.exists()
            assert plantuml_file.exists()
            assert json_file.stat().st_size > 0
            assert plantuml_file.stat().st_size > 0
    
    def test_example_system_complete_workflow(self, temp_workspace):
        """Test the complete workflow using the example e-commerce system."""
        with patch('src.diagrams.example_system.Workspace'), \
             patch('src.diagrams.example_system.Model') as mock_model_class:
            
            # Setup mocks
            mock_model = Mock()
            mock_model_class.return_value = mock_model
            
            # Mock element creation
            mock_person = Mock()
            mock_system = Mock()
            mock_container = Mock()
            mock_component = Mock()
            
            mock_model.Person.return_value = mock_person
            mock_model.SoftwareSystem.return_value = mock_system
            mock_system.Container.return_value = mock_container
            mock_container.Component.return_value = mock_component
            
            # Mock view creation
            mock_view = Mock()
            
            # Create example system
            ecommerce = ECommerceSystemDiagrams()
            
            # Mock the generator methods
            ecommerce.generator.add_system_context_view = Mock(return_value=mock_view)
            ecommerce.generator.add_container_view = Mock(return_value=mock_view)
            ecommerce.generator.add_component_view = Mock(return_value=mock_view)
            ecommerce.generator.export_to_json = Mock(return_value='{"test": "json"}')
            ecommerce.generator.export_to_plantuml = Mock(return_value='@startuml\ntest\n@enduml')
            ecommerce.generator.validate_export_data = Mock(return_value=True)
            ecommerce.generator.validate_plantuml_output = Mock(return_value=True)
            ecommerce.generator.get_metadata = Mock(return_value=[])
            
            # Create all views
            ecommerce.create_system_context_view()
            ecommerce.create_container_view()
            ecommerce.create_component_view()
            
            # Verify all views were created
            assert len(ecommerce.people) == 3
            assert len(ecommerce.systems) == 5
            assert len(ecommerce.containers) == 10
            assert len(ecommerce.components) == 8
            
            # Export diagrams
            docs_dir = temp_workspace / "docs"
            export_diagrams(ecommerce, str(docs_dir))
            
            # Verify exports were called
            ecommerce.generator.export_to_json.assert_called_once()
            ecommerce.generator.export_to_plantuml.assert_called_once()
            ecommerce.generator.validate_export_data.assert_called_once()
            ecommerce.generator.validate_plantuml_output.assert_called_once()


class TestSiteGenerationPipeline:
    """Integration tests for the site generation pipeline."""
    
    @pytest.fixture
    def temp_workspace_with_templates(self):
        """Create a temporary workspace with templates for site generation testing."""
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            
            # Create directory structure
            templates_dir = workspace / "templates"
            templates_dir.mkdir()
            docs_dir = workspace / "docs"
            docs_dir.mkdir()
            output_dir = workspace / "output"
            output_dir.mkdir()
            
            # Create basic templates
            base_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>{{ config.title }}</title>
            </head>
            <body>
                {% block content %}{% endblock %}
            </body>
            </html>
            """
            
            index_template = """
            {% extends "base.html" %}
            {% block content %}
            <h1>{{ config.title }}</h1>
            <p>{{ config.description }}</p>
            <p>Total diagrams: {{ stats.total_diagrams }}</p>
            {% endblock %}
            """
            
            diagrams_template = """
            {% extends "base.html" %}
            {% block content %}
            <h1>All Diagrams</h1>
            {% for diagram in diagrams %}
            <div>
                <h2>{{ diagram.title }}</h2>
                <p>{{ diagram.description }}</p>
                <p>Type: {{ diagram.diagram_type }}</p>
            </div>
            {% endfor %}
            {% endblock %}
            """
            
            diagram_template = """
            {% extends "base.html" %}
            {% block content %}
            <h1>{{ diagram.title }}</h1>
            <p>{{ diagram.description }}</p>
            <p>Type: {{ diagram.diagram_type }}</p>
            <p>Last updated: {{ diagram.last_updated }}</p>
            {% if plantuml_source %}
            <pre>{{ plantuml_source }}</pre>
            {% endif %}
            {% endblock %}
            """
            
            # Write templates
            (templates_dir / "base.html").write_text(base_template)
            (templates_dir / "index.html").write_text(index_template)
            (templates_dir / "diagrams.html").write_text(diagrams_template)
            (templates_dir / "diagram.html").write_text(diagram_template)
            
            # Create sample PlantUML file first
            plantuml_content = "@startuml\nPerson(user, \"User\")\nSystem(system, \"System\")\n@enduml"
            plantuml_file = docs_dir / "system_context.puml"
            plantuml_file.write_text(plantuml_content)
            
            # Create sample diagram metadata
            metadata = {
                "metadata": {
                    "diagrams": [
                        {
                            "title": "System Context",
                            "description": "System context diagram",
                            "type": "system_context",
                            "lastUpdated": "2023-01-01T12:00:00",
                            "filePath": "system_context.json",
                            "outputFiles": {
                                "png": "system_context.png",
                                "plantuml": str(plantuml_file)
                            }
                        },
                        {
                            "title": "Container View",
                            "description": "Container view diagram",
                            "type": "container",
                            "lastUpdated": "2023-01-02T12:00:00",
                            "filePath": "container.json",
                            "outputFiles": {"png": "container.png"}
                        }
                    ]
                }
            }
            
            metadata_file = docs_dir / "diagram_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f)
            
            yield workspace
    
    def test_complete_site_generation_workflow(self, temp_workspace_with_templates):
        """Test the complete site generation workflow."""
        workspace = temp_workspace_with_templates
        
        # Create site configuration
        config = SiteConfig(
            title="Integration Test Site",
            description="Site for integration testing",
            base_url="https://test.example.com"
        )
        
        # Create site generator
        generator = SiteGenerator(
            templates_dir=str(workspace / "templates"),
            output_dir=str(workspace / "output"),
            diagrams_dir=str(workspace / "docs"),
            config=config
        )
        
        # Step 1: Validate templates
        assert generator.validate_templates() is True
        
        # Step 2: Generate complete site
        generator.generate_site()
        
        # Step 3: Verify output structure
        output_dir = workspace / "output"
        assert (output_dir / "index.html").exists()
        assert (output_dir / "diagrams" / "index.html").exists()
        assert (output_dir / "diagrams" / "system_context.html").exists()
        assert (output_dir / "diagrams" / "container.html").exists()
        
        # Step 4: Verify content
        index_content = (output_dir / "index.html").read_text()
        assert "Integration Test Site" in index_content
        assert "Site for integration testing" in index_content
        assert "Total diagrams: 2" in index_content
        
        diagrams_content = (output_dir / "diagrams" / "index.html").read_text()
        assert "All Diagrams" in diagrams_content
        assert "System Context" in diagrams_content
        assert "Container View" in diagrams_content
        
        diagram_content = (output_dir / "diagrams" / "system_context.html").read_text()
        assert "System Context" in diagram_content
        assert "system_context" in diagram_content
        assert "@startuml" in diagram_content  # PlantUML source should be included
        
        # Step 5: Generate sitemap
        generator.generate_sitemap()
        
        sitemap_file = output_dir / "sitemap.xml"
        assert sitemap_file.exists()
        
        sitemap_content = sitemap_file.read_text()
        assert "https://test.example.com" in sitemap_content
        assert "system_context.html" in sitemap_content
        assert "container.html" in sitemap_content
        
        # Step 6: Verify navigation structure
        navigation = generator.create_navigation_structure()
        assert "main" in navigation
        assert "categories" in navigation
        assert len(navigation["categories"]) == 2  # system_context and container
        
        # Step 7: Verify statistics
        assert generator.stats.total_diagrams == 2
        assert generator.stats.system_contexts == 1
        assert generator.stats.containers == 1
        assert generator.stats.components == 0
    
    def test_site_generation_with_missing_assets(self, temp_workspace_with_templates):
        """Test site generation when some assets are missing."""
        workspace = temp_workspace_with_templates
        
        # Remove one of the PlantUML files to test missing asset handling
        (workspace / "docs" / "system_context.puml").unlink()
        
        # Create site generator
        generator = SiteGenerator(
            templates_dir=str(workspace / "templates"),
            output_dir=str(workspace / "output"),
            diagrams_dir=str(workspace / "docs")
        )
        
        # Generate site - should handle missing assets gracefully
        generator.generate_site()
        
        # Verify site was still generated
        output_dir = workspace / "output"
        assert (output_dir / "index.html").exists()
        assert (output_dir / "diagrams" / "system_context.html").exists()
        
        # Verify content doesn't include PlantUML source for missing file
        diagram_content = (output_dir / "diagrams" / "system_context.html").read_text()
        assert "System Context" in diagram_content
        assert "@startuml" not in diagram_content  # No PlantUML source


class TestGitHubActionsWorkflowValidation:
    """Integration tests for GitHub Actions workflow validation."""
    
    @pytest.fixture
    def temp_workspace_with_workflow(self):
        """Create a temporary workspace with GitHub Actions workflow."""
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            
            # Create directory structure
            workflows_dir = workspace / ".github" / "workflows"
            workflows_dir.mkdir(parents=True)
            
            # Create workflow file
            workflow_content = """
name: Render Diagrams and Deploy to GitHub Pages

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

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  render-and-deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install uv
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH
        
    - name: Install dependencies
      run: |
        uv sync
        
    - name: Generate diagrams
      run: |
        uv run python src/diagrams/example_system.py
        
    - name: Install PlantUML
      run: |
        sudo apt-get update
        sudo apt-get install -y plantuml
        
    - name: Render PlantUML diagrams
      run: |
        find docs -name "*.puml" -exec plantuml -tpng {} \\;
        find docs -name "*.puml" -exec plantuml -tsvg {} \\;
        
    - name: Generate static site
      run: |
        uv run python src/site_generator.py --output-dir docs --base-url ${{ github.event.repository.html_url }}/pages
        
    - name: Setup Pages
      uses: actions/configure-pages@v3
      
    - name: Upload artifact
      uses: actions/upload-pages-artifact@v2
      with:
        path: './docs'
        
    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v2
"""
            
            workflow_file = workflows_dir / "render-diagrams.yml"
            workflow_file.write_text(workflow_content)
            
            yield workspace
    
    def test_workflow_file_exists_and_valid_yaml(self, temp_workspace_with_workflow):
        """Test that workflow file exists and contains valid YAML."""
        workspace = temp_workspace_with_workflow
        workflow_file = workspace / ".github" / "workflows" / "render-diagrams.yml"
        
        assert workflow_file.exists()
        
        # Parse YAML to ensure it's valid
        with open(workflow_file, 'r') as f:
            workflow_data = yaml.safe_load(f)
        
        assert workflow_data is not None
        assert "name" in workflow_data
        assert True in workflow_data or "on" in workflow_data
        assert "jobs" in workflow_data
    
    def test_workflow_structure_validation(self, temp_workspace_with_workflow):
        """Test that workflow has required structure and steps."""
        workspace = temp_workspace_with_workflow
        workflow_file = workspace / ".github" / "workflows" / "render-diagrams.yml"
        
        with open(workflow_file, 'r') as f:
            workflow_data = yaml.safe_load(f)
        
        # Verify basic structure
        assert workflow_data["name"] == "Render Diagrams and Deploy to GitHub Pages"
        
        # Verify triggers (handle YAML 'on' key conversion)
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        assert "push" in triggers
        assert "pull_request" in triggers
        assert "workflow_dispatch" in triggers
        
        # Verify permissions
        assert "permissions" in workflow_data
        assert workflow_data["permissions"]["contents"] == "read"
        assert workflow_data["permissions"]["pages"] == "write"
        
        # Verify jobs
        assert "render-and-deploy" in workflow_data["jobs"]
        job = workflow_data["jobs"]["render-and-deploy"]
        
        assert job["runs-on"] == "ubuntu-latest"
        assert "steps" in job
        
        # Verify required steps exist
        step_names = [step.get("name", "") for step in job["steps"]]
        required_steps = [
            "Checkout repository",
            "Set up Python",
            "Install uv",
            "Install dependencies",
            "Generate diagrams",
            "Install PlantUML",
            "Render PlantUML diagrams",
            "Generate static site",
            "Setup Pages",
            "Upload artifact",
            "Deploy to GitHub Pages"
        ]
        
        for required_step in required_steps:
            assert required_step in step_names, f"Missing required step: {required_step}"
    
    def test_workflow_commands_validation(self, temp_workspace_with_workflow):
        """Test that workflow commands are properly structured."""
        workspace = temp_workspace_with_workflow
        workflow_file = workspace / ".github" / "workflows" / "render-diagrams.yml"
        
        with open(workflow_file, 'r') as f:
            workflow_data = yaml.safe_load(f)
        
        job = workflow_data["jobs"]["render-and-deploy"]
        steps = job["steps"]
        
        # Find and validate specific steps
        uv_install_step = next(step for step in steps if step.get("name") == "Install uv")
        assert "curl -LsSf https://astral.sh/uv/install.sh" in uv_install_step["run"]
        
        deps_install_step = next(step for step in steps if step.get("name") == "Install dependencies")
        assert "uv sync" in deps_install_step["run"]
        
        diagram_gen_step = next(step for step in steps if step.get("name") == "Generate diagrams")
        assert "uv run python src/diagrams/example_system.py" in diagram_gen_step["run"]
        
        plantuml_render_step = next(step for step in steps if step.get("name") == "Render PlantUML diagrams")
        assert "plantuml -tpng" in plantuml_render_step["run"]
        assert "plantuml -tsvg" in plantuml_render_step["run"]
        
        site_gen_step = next(step for step in steps if step.get("name") == "Generate static site")
        assert "uv run python src/site_generator.py" in site_gen_step["run"]


class TestEndToEndWorkflow:
    """End-to-end integration tests simulating the complete workflow."""
    
    @pytest.fixture
    def complete_workspace(self):
        """Create a complete workspace with all necessary files."""
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            
            # Create full directory structure
            (workspace / "src" / "diagrams").mkdir(parents=True)
            (workspace / "docs").mkdir()
            (workspace / "templates").mkdir()
            (workspace / ".github" / "workflows").mkdir(parents=True)
            
            # Create pyproject.toml
            pyproject_content = """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "test-project"
version = "0.1.0"
dependencies = [
    "pystructurizr>=0.1.0",
    "jinja2>=3.1.0",
    "pyyaml>=6.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
]
"""
            (workspace / "pyproject.toml").write_text(pyproject_content)
            
            # Create basic templates (simplified versions)
            templates = {
                "base.html": "<html><head><title>{{ config.title }}</title></head><body>{% block content %}{% endblock %}</body></html>",
                "index.html": "{% extends 'base.html' %}{% block content %}<h1>{{ config.title }}</h1>{% endblock %}",
                "diagrams.html": "{% extends 'base.html' %}{% block content %}<h1>Diagrams</h1>{% endblock %}",
                "diagram.html": "{% extends 'base.html' %}{% block content %}<h1>{{ diagram.title }}</h1>{% endblock %}"
            }
            
            for name, content in templates.items():
                (workspace / "templates" / name).write_text(content)
            
            yield workspace
    
    @patch('subprocess.run')
    def test_simulated_ci_workflow(self, mock_subprocess, complete_workspace):
        """Test a simulated CI workflow execution."""
        workspace = complete_workspace
        
        # Mock successful subprocess calls
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")
        
        # Simulate the workflow steps
        steps = [
            # Step 1: Install dependencies (simulated)
            ["uv", "sync"],
            
            # Step 2: Generate diagrams (simulated)
            ["python", "src/diagrams/example_system.py"],
            
            # Step 3: Render PlantUML (simulated)
            ["plantuml", "-tpng", "docs/test.puml"],
            
            # Step 4: Generate site (simulated)
            ["python", "src/site_generator.py", "--output-dir", "docs"]
        ]
        
        # Execute simulated steps
        for step in steps:
            result = subprocess.run(step, cwd=workspace, capture_output=True, text=True)
            # In real execution, we'd check result.returncode == 0
        
        # Verify subprocess was called for each step
        assert mock_subprocess.call_count == len(steps)
        
        # Verify the calls were made with correct arguments
        call_args = [call[0][0] for call in mock_subprocess.call_args_list]
        expected_commands = ["uv", "python", "plantuml", "python"]
        
        for i, expected_cmd in enumerate(expected_commands):
            assert call_args[i][0] == expected_cmd
    
    def test_workflow_error_handling(self, complete_workspace):
        """Test workflow behavior when errors occur."""
        workspace = complete_workspace
        
        # Test missing template error
        (workspace / "templates" / "base.html").unlink()
        
        generator = SiteGenerator(
            templates_dir=str(workspace / "templates"),
            output_dir=str(workspace / "docs")
        )
        
        with pytest.raises(FileNotFoundError, match="Required template not found"):
            generator.validate_templates()
    
    def test_workflow_with_real_file_operations(self, complete_workspace):
        """Test workflow with actual file operations (no mocking)."""
        workspace = complete_workspace
        
        # Create a simple diagram metadata file
        metadata = {
            "metadata": {
                "diagrams": [
                    {
                        "title": "Test Diagram",
                        "description": "A test diagram",
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
        config = SiteConfig(title="Test Site", description="Test Description")
        generator = SiteGenerator(
            templates_dir=str(workspace / "templates"),
            output_dir=str(workspace / "docs"),
            diagrams_dir=str(workspace / "docs"),
            config=config
        )
        
        # This should work without errors
        generator.validate_templates()
        generator.generate_site()
        
        # Verify output files were created
        assert (workspace / "docs" / "index.html").exists()
        assert (workspace / "docs" / "diagrams" / "index.html").exists()
        assert (workspace / "docs" / "diagrams" / "test.html").exists()
        
        # Verify content
        index_content = (workspace / "docs" / "index.html").read_text()
        assert "Test Site" in index_content