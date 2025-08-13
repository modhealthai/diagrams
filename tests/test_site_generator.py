"""
Unit tests for the SiteGenerator class.

Tests cover site configuration, metadata loading, template processing,
page generation, and static asset handling.
"""

import pytest
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
from tempfile import TemporaryDirectory
import os

from src.site_generator import (
    SiteGenerator,
    SiteConfig,
    SiteStats,
)
from src.diagrams.generator import DiagramMetadata


class TestSiteConfig:
    """Test cases for SiteConfig dataclass."""
    
    def test_site_config_creation_with_defaults(self):
        """Test creating SiteConfig with default values."""
        config = SiteConfig()
        
        assert config.title == "Architecture Diagrams"
        assert config.description == "Explore our system architecture through interactive diagrams"
        assert config.base_url == ""
        assert config.theme == "default"
        assert len(config.navigation) == 2
        assert config.navigation[0]["name"] == "Home"
        assert config.navigation[1]["name"] == "All Diagrams"
    
    def test_site_config_creation_with_custom_values(self):
        """Test creating SiteConfig with custom values."""
        custom_nav = [{"name": "Custom", "url": "/custom"}]
        
        config = SiteConfig(
            title="Custom Title",
            description="Custom description",
            base_url="https://example.com",
            theme="custom",
            navigation=custom_nav
        )
        
        assert config.title == "Custom Title"
        assert config.description == "Custom description"
        assert config.base_url == "https://example.com"
        assert config.theme == "custom"
        assert config.navigation == custom_nav


class TestSiteStats:
    """Test cases for SiteStats dataclass."""
    
    def test_site_stats_creation_with_defaults(self):
        """Test creating SiteStats with default values."""
        stats = SiteStats()
        
        assert stats.total_diagrams == 0
        assert stats.system_contexts == 0
        assert stats.containers == 0
        assert stats.components == 0
        assert stats.last_updated is None
    
    def test_site_stats_creation_with_values(self):
        """Test creating SiteStats with specific values."""
        last_updated = datetime.now()
        
        stats = SiteStats(
            total_diagrams=10,
            system_contexts=3,
            containers=4,
            components=3,
            last_updated=last_updated
        )
        
        assert stats.total_diagrams == 10
        assert stats.system_contexts == 3
        assert stats.containers == 4
        assert stats.components == 3
        assert stats.last_updated == last_updated


class TestSiteGenerator:
    """Test cases for SiteGenerator class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def config(self):
        """Create a test site configuration."""
        return SiteConfig(
            title="Test Site",
            description="Test site description",
            base_url="https://test.example.com"
        )
    
    @pytest.fixture
    def sample_diagrams(self):
        """Create sample diagram metadata for testing."""
        return [
            DiagramMetadata(
                title="System Context",
                description="System context diagram",
                diagram_type="system_context",
                last_updated=datetime(2023, 1, 1, 12, 0, 0),
                file_path="system_context.json",
                output_files={"png": "system_context.png", "plantuml": "system_context.puml"}
            ),
            DiagramMetadata(
                title="Container View",
                description="Container view diagram",
                diagram_type="container",
                last_updated=datetime(2023, 1, 2, 12, 0, 0),
                file_path="container.json",
                output_files={"png": "container.png"}
            ),
            DiagramMetadata(
                title="Component View",
                description="Component view diagram",
                diagram_type="component",
                last_updated=datetime(2023, 1, 3, 12, 0, 0),
                file_path="component.json",
                output_files={}
            )
        ]
    
    def test_site_generator_initialization(self, temp_dir, config):
        """Test SiteGenerator initialization."""
        templates_dir = temp_dir / "templates"
        output_dir = temp_dir / "output"
        diagrams_dir = temp_dir / "diagrams"
        
        generator = SiteGenerator(
            templates_dir=str(templates_dir),
            output_dir=str(output_dir),
            diagrams_dir=str(diagrams_dir),
            config=config
        )
        
        assert generator.templates_dir == templates_dir
        assert generator.output_dir == output_dir
        assert generator.diagrams_dir == diagrams_dir
        assert generator.config == config
        assert generator.diagrams == []
        assert generator.stats.total_diagrams == 0
    
    def test_site_generator_initialization_with_defaults(self, temp_dir):
        """Test SiteGenerator initialization with default values."""
        generator = SiteGenerator()
        
        assert generator.templates_dir == Path("templates")
        assert generator.output_dir == Path("docs")
        assert generator.diagrams_dir == Path("docs")
        assert isinstance(generator.config, SiteConfig)
        assert generator.config.title == "Architecture Diagrams"
    
    def test_load_diagram_metadata_from_metadata_file(self, temp_dir):
        """Test loading diagram metadata from metadata file."""
        diagrams_dir = temp_dir / "diagrams"
        diagrams_dir.mkdir()
        
        # Create metadata file
        metadata_content = {
            "metadata": {
                "diagrams": [
                    {
                        "title": "Test Diagram",
                        "description": "Test description",
                        "type": "system_context",
                        "lastUpdated": "2023-01-01T12:00:00",
                        "filePath": "test.json",
                        "outputFiles": {"png": "test.png"}
                    }
                ]
            }
        }
        
        metadata_file = diagrams_dir / "diagram_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata_content, f)
        
        generator = SiteGenerator(diagrams_dir=str(diagrams_dir))
        generator.load_diagram_metadata()
        
        assert len(generator.diagrams) == 1
        diagram = generator.diagrams[0]
        assert diagram.title == "Test Diagram"
        assert diagram.description == "Test description"
        assert diagram.diagram_type == "system_context"
        assert diagram.file_path == "test.json"
        assert diagram.output_files == {"png": "test.png"}
    
    def test_load_diagram_metadata_from_individual_files(self, temp_dir):
        """Test loading diagram metadata from individual JSON files."""
        diagrams_dir = temp_dir / "diagrams"
        diagrams_dir.mkdir()
        
        # Create individual diagram file
        diagram_content = {
            "workspace": {
                "name": "Test Workspace",
                "description": "Test description"
            },
            "metadata": {
                "diagrams": [
                    {
                        "title": "Individual Diagram",
                        "description": "Individual description",
                        "type": "container",
                        "lastUpdated": "2023-01-02T12:00:00",
                        "filePath": "individual.json",
                        "outputFiles": {}
                    }
                ]
            }
        }
        
        diagram_file = diagrams_dir / "individual_diagram.json"
        with open(diagram_file, 'w') as f:
            json.dump(diagram_content, f)
        
        generator = SiteGenerator(diagrams_dir=str(diagrams_dir))
        generator.load_diagram_metadata()
        
        assert len(generator.diagrams) == 1
        diagram = generator.diagrams[0]
        assert diagram.title == "Individual Diagram"
        assert diagram.diagram_type == "container"
    
    def test_load_diagram_metadata_invalid_json(self, temp_dir, capfd):
        """Test loading diagram metadata with invalid JSON."""
        diagrams_dir = temp_dir / "diagrams"
        diagrams_dir.mkdir()
        
        # Create invalid JSON file
        invalid_file = diagrams_dir / "invalid.json"
        with open(invalid_file, 'w') as f:
            f.write("{ invalid json }")
        
        generator = SiteGenerator(diagrams_dir=str(diagrams_dir))
        generator.load_diagram_metadata()
        
        # Should handle error gracefully
        assert len(generator.diagrams) == 0
        
        # Check warning was printed
        captured = capfd.readouterr()
        assert "Warning: Could not process" in captured.out
    
    def test_calculate_stats(self, temp_dir, sample_diagrams):
        """Test calculation of site statistics."""
        generator = SiteGenerator(diagrams_dir=str(temp_dir))
        generator.diagrams = sample_diagrams
        generator._calculate_stats()
        
        assert generator.stats.total_diagrams == 3
        assert generator.stats.system_contexts == 1
        assert generator.stats.containers == 1
        assert generator.stats.components == 1
        assert generator.stats.last_updated == datetime(2023, 1, 3, 12, 0, 0)
    
    def test_calculate_stats_empty_diagrams(self, temp_dir):
        """Test calculation of stats with no diagrams."""
        generator = SiteGenerator(diagrams_dir=str(temp_dir))
        generator.diagrams = []
        generator._calculate_stats()
        
        assert generator.stats.total_diagrams == 0
        assert generator.stats.system_contexts == 0
        assert generator.stats.containers == 0
        assert generator.stats.components == 0
        assert generator.stats.last_updated is None
    
    def test_create_output_structure(self, temp_dir):
        """Test creation of output directory structure."""
        output_dir = temp_dir / "output"
        
        generator = SiteGenerator(output_dir=str(output_dir))
        generator._create_output_structure()
        
        assert output_dir.exists()
        assert (output_dir / "diagrams").exists()
    
    def test_generate_index_page(self, temp_dir, sample_diagrams):
        """Test generation of index page."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        # Mock Jinja2 environment and template
        mock_template = Mock()
        mock_template.render.return_value = "<html>Test Index</html>"
        mock_env_instance = Mock()
        mock_env_instance.get_template.return_value = mock_template
        mock_env_instance.filters = {}  # Make filters assignable
        
        generator = SiteGenerator(output_dir=str(output_dir))
        generator.jinja_env = mock_env_instance
        generator.diagrams = sample_diagrams
        generator._calculate_stats()
        
        generator._generate_index_page()
        
        # Check template was called
        mock_env_instance.get_template.assert_called_with("index.html")
        mock_template.render.assert_called_once()
        
        # Check file was created
        index_file = output_dir / "index.html"
        assert index_file.exists()
        assert index_file.read_text() == "<html>Test Index</html>"
    
    def test_generate_diagrams_listing_page(self, temp_dir, sample_diagrams):
        """Test generation of diagrams listing page."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        # Mock Jinja2 environment and template
        mock_template = Mock()
        mock_template.render.return_value = "<html>Diagrams List</html>"
        mock_env_instance = Mock()
        mock_env_instance.get_template.return_value = mock_template
        mock_env_instance.filters = {}  # Make filters assignable
        
        generator = SiteGenerator(output_dir=str(output_dir))
        generator.jinja_env = mock_env_instance
        generator.diagrams = sample_diagrams
        generator._calculate_stats()
        
        generator._generate_diagrams_listing_page()
        
        # Check template was called
        mock_env_instance.get_template.assert_called_with("diagrams.html")
        mock_template.render.assert_called_once()
        
        # Check file was created
        diagrams_file = output_dir / "diagrams" / "index.html"
        assert diagrams_file.exists()
        assert diagrams_file.read_text() == "<html>Diagrams List</html>"
    
    def test_generate_individual_diagram_pages(self, temp_dir, sample_diagrams):
        """Test generation of individual diagram pages."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        (output_dir / "diagrams").mkdir()
        
        # Mock Jinja2 environment and template
        mock_template = Mock()
        mock_template.render.return_value = "<html>Diagram Page</html>"
        mock_env_instance = Mock()
        mock_env_instance.get_template.return_value = mock_template
        mock_env_instance.filters = {}  # Make filters assignable
        
        generator = SiteGenerator(output_dir=str(output_dir))
        generator.jinja_env = mock_env_instance
        generator.diagrams = sample_diagrams
        
        generator._generate_individual_diagram_pages()
        
        # Check template was called for each diagram
        assert mock_env_instance.get_template.call_count == 3
        assert mock_template.render.call_count == 3
        
        # Check files were created
        assert (output_dir / "diagrams" / "system_context.html").exists()
        assert (output_dir / "diagrams" / "container.html").exists()
        assert (output_dir / "diagrams" / "component.html").exists()
    
    def test_find_related_diagrams(self, temp_dir, sample_diagrams):
        """Test finding related diagrams."""
        generator = SiteGenerator(diagrams_dir=str(temp_dir))
        generator.diagrams = sample_diagrams
        
        current_diagram = sample_diagrams[0]  # system_context
        related = generator._find_related_diagrams(current_diagram)
        
        # Should not include the current diagram
        assert current_diagram not in related
        # Should include other diagrams
        assert len(related) <= 4
        assert all(d != current_diagram for d in related)
    
    def test_load_plantuml_source_existing_file(self, temp_dir):
        """Test loading PlantUML source from existing file."""
        # Create PlantUML file
        plantuml_file = temp_dir / "test.puml"
        plantuml_content = "@startuml\nPerson(user, \"User\")\n@enduml"
        plantuml_file.write_text(plantuml_content)
        
        diagram = DiagramMetadata(
            title="Test",
            description="Test",
            diagram_type="system_context",
            last_updated=datetime.now(),
            file_path="test.json",
            output_files={"plantuml": str(plantuml_file)}
        )
        
        generator = SiteGenerator(diagrams_dir=str(temp_dir))
        result = generator._load_plantuml_source(diagram)
        
        assert result == plantuml_content
    
    def test_load_plantuml_source_missing_file(self, temp_dir):
        """Test loading PlantUML source from missing file."""
        diagram = DiagramMetadata(
            title="Test",
            description="Test",
            diagram_type="system_context",
            last_updated=datetime.now(),
            file_path="test.json",
            output_files={"plantuml": "nonexistent.puml"}
        )
        
        generator = SiteGenerator(diagrams_dir=str(temp_dir))
        result = generator._load_plantuml_source(diagram)
        
        assert result is None
    
    def test_load_plantuml_source_no_plantuml_output(self, temp_dir):
        """Test loading PlantUML source when no PlantUML output exists."""
        diagram = DiagramMetadata(
            title="Test",
            description="Test",
            diagram_type="system_context",
            last_updated=datetime.now(),
            file_path="test.json",
            output_files={"png": "test.png"}  # No plantuml output
        )
        
        generator = SiteGenerator(diagrams_dir=str(temp_dir))
        result = generator._load_plantuml_source(diagram)
        
        assert result is None
    
    @patch('src.site_generator.shutil.copy2')
    def test_copy_static_assets(self, mock_copy, temp_dir, sample_diagrams):
        """Test copying static assets."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        # Create source files
        source_file = temp_dir / "system_context.png"
        source_file.write_text("fake image content")
        
        # Update diagram to point to existing file
        sample_diagrams[0].output_files["png"] = str(source_file)
        
        generator = SiteGenerator(
            output_dir=str(output_dir),
            diagrams_dir=str(temp_dir)
        )
        generator.diagrams = sample_diagrams
        
        generator._copy_static_assets()
        
        # Should have attempted to copy the file
        mock_copy.assert_called()
    
    def test_create_navigation_structure(self, temp_dir, sample_diagrams):
        """Test creation of navigation structure."""
        generator = SiteGenerator(diagrams_dir=str(temp_dir))
        generator.diagrams = sample_diagrams
        
        navigation = generator.create_navigation_structure()
        
        assert "main" in navigation
        assert "categories" in navigation
        
        # Check main navigation
        assert len(navigation["main"]) == 2
        assert navigation["main"][0]["name"] == "Home"
        assert navigation["main"][1]["name"] == "All Diagrams"
        
        # Check categories
        assert "system_context" in navigation["categories"]
        assert "container" in navigation["categories"]
        assert "component" in navigation["categories"]
        
        # Check category details
        system_context_cat = navigation["categories"]["system_context"]
        assert system_context_cat["name"] == "System Context"
        assert system_context_cat["count"] == 1
        assert len(system_context_cat["diagrams"]) == 1
    
    def test_validate_templates_success(self, temp_dir):
        """Test successful template validation."""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()
        
        # Create required templates
        required_templates = ["base.html", "index.html", "diagrams.html", "diagram.html"]
        for template_name in required_templates:
            (templates_dir / template_name).write_text(f"<html>{template_name}</html>")
        
        generator = SiteGenerator(templates_dir=str(templates_dir))
        result = generator.validate_templates()
        
        assert result is True
    
    def test_validate_templates_missing_template(self, temp_dir):
        """Test template validation with missing template."""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()
        
        # Create only some templates
        (templates_dir / "base.html").write_text("<html>base</html>")
        # Missing other required templates
        
        generator = SiteGenerator(templates_dir=str(templates_dir))
        
        with pytest.raises(FileNotFoundError, match="Required template not found"):
            generator.validate_templates()
    
    def test_generate_sitemap(self, temp_dir, sample_diagrams, config):
        """Test sitemap generation."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        generator = SiteGenerator(
            output_dir=str(output_dir),
            config=config
        )
        generator.diagrams = sample_diagrams
        
        generator.generate_sitemap()
        
        sitemap_file = output_dir / "sitemap.xml"
        assert sitemap_file.exists()
        
        sitemap_content = sitemap_file.read_text()
        assert "<?xml version=" in sitemap_content
        assert "<urlset" in sitemap_content
        assert config.base_url in sitemap_content
        assert "system_context.html" in sitemap_content
        assert "container.html" in sitemap_content
        assert "component.html" in sitemap_content
    
    @patch('src.site_generator.SiteGenerator.load_diagram_metadata')
    @patch('src.site_generator.SiteGenerator._create_output_structure')
    @patch('src.site_generator.SiteGenerator._generate_index_page')
    @patch('src.site_generator.SiteGenerator._generate_diagrams_listing_page')
    @patch('src.site_generator.SiteGenerator._generate_individual_diagram_pages')
    @patch('src.site_generator.SiteGenerator._copy_static_assets')
    def test_generate_site_complete_workflow(
        self,
        mock_copy_assets,
        mock_generate_individual,
        mock_generate_listing,
        mock_generate_index,
        mock_create_structure,
        mock_load_metadata,
        temp_dir,
        sample_diagrams
    ):
        """Test complete site generation workflow."""
        generator = SiteGenerator(diagrams_dir=str(temp_dir))
        generator.diagrams = sample_diagrams  # Set diagrams for the test
        
        generator.generate_site()
        
        # Verify all steps were called in order
        mock_load_metadata.assert_called_once()
        mock_create_structure.assert_called_once()
        mock_generate_index.assert_called_once()
        mock_generate_listing.assert_called_once()
        mock_generate_individual.assert_called_once()
        mock_copy_assets.assert_called_once()
    
    def test_jinja_environment_setup(self, temp_dir):
        """Test that Jinja2 environment is properly configured."""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()
        
        generator = SiteGenerator(templates_dir=str(templates_dir))
        
        # Check that environment is configured
        assert generator.jinja_env is not None
        assert 'replace' in generator.jinja_env.filters
        
        # Test custom filter
        result = generator.jinja_env.filters['replace']("hello world", "world", "test")
        assert result == "hello test"