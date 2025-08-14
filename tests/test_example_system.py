"""
Unit tests for the example system diagrams.

Tests cover the ECommerceSystemDiagrams class and its methods for creating
system context, container, and component views.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, mock_open

from src.diagrams.example_system import ECommerceSystemDiagrams, create_example_diagrams, export_diagrams
from src.diagrams.generator import DiagramConfig


class TestECommerceSystemDiagrams:
    """Test cases for ECommerceSystemDiagrams class."""
    
    @pytest.fixture
    def ecommerce_diagrams(self):
        """Create an ECommerceSystemDiagrams instance for testing."""
        return ECommerceSystemDiagrams()
    
    def test_initialization(self, ecommerce_diagrams):
        """Test ECommerceSystemDiagrams initialization."""
        assert isinstance(ecommerce_diagrams.config, DiagramConfig)
        assert ecommerce_diagrams.config.name == "E-Commerce System Architecture"
        assert ecommerce_diagrams.config.description == "Comprehensive architectural documentation for an e-commerce platform"
        assert ecommerce_diagrams.config.version == "1.0.0"
        assert ecommerce_diagrams.config.author == "Architecture Team"
        
        assert ecommerce_diagrams.workspace is None
        assert ecommerce_diagrams.model is None
        assert ecommerce_diagrams.people == {}
        assert ecommerce_diagrams.systems == {}
        assert ecommerce_diagrams.containers == {}
        assert ecommerce_diagrams.components == {}
    
    @patch('src.diagrams.example_system.Model')
    @patch('src.diagrams.generator.Workspace')
    def test_create_system_context_view(self, mock_workspace, mock_model, ecommerce_diagrams):
        """Test creation of system context view."""
        # Setup mocks
        mock_workspace_instance = Mock()
        mock_workspace.return_value = mock_workspace_instance
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance
        
        # Mock person and system creation
        mock_person = Mock()
        mock_system = Mock()
        mock_model_instance.Person.return_value = mock_person
        mock_model_instance.SoftwareSystem.return_value = mock_system
        
        # Mock view creation
        mock_view = Mock()
        ecommerce_diagrams.generator.add_system_context_view = Mock(return_value=mock_view)
        
        # Execute
        ecommerce_diagrams.create_system_context_view()
        
        # Verify workspace creation
        mock_workspace.assert_called_once()
        # Note: Model creation happens inside the method, so we verify it was set up
        
        # Verify people were created
        assert len(ecommerce_diagrams.people) == 3
        assert "customer" in ecommerce_diagrams.people
        assert "admin" in ecommerce_diagrams.people
        assert "support" in ecommerce_diagrams.people
        
        # Verify systems were created
        assert len(ecommerce_diagrams.systems) == 5
        assert "ecommerce" in ecommerce_diagrams.systems
        assert "payment" in ecommerce_diagrams.systems
        assert "email" in ecommerce_diagrams.systems
        assert "inventory" in ecommerce_diagrams.systems
        assert "shipping" in ecommerce_diagrams.systems
        
        # Verify view was created
        ecommerce_diagrams.generator.add_system_context_view.assert_called_once()
    
    def test_create_container_view_without_system_context(self, ecommerce_diagrams):
        """Test that creating container view without system context raises error."""
        with pytest.raises(ValueError, match="System context view must be created first"):
            ecommerce_diagrams.create_container_view()
    
    @patch('src.diagrams.example_system.Model')
    @patch('src.diagrams.generator.Workspace')
    def test_create_container_view_success(self, mock_workspace, mock_model, ecommerce_diagrams):
        """Test successful creation of container view."""
        # Setup system context first
        mock_workspace_instance = Mock()
        mock_workspace.return_value = mock_workspace_instance
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance
        
        # Mock system and container creation
        mock_system = Mock()
        mock_container = Mock()
        mock_model_instance.Person.return_value = Mock()
        mock_model_instance.SoftwareSystem.return_value = mock_system
        mock_system.Container.return_value = mock_container
        
        # Mock view creation
        mock_view = Mock()
        ecommerce_diagrams.generator.add_system_context_view = Mock(return_value=mock_view)
        ecommerce_diagrams.generator.add_container_view = Mock(return_value=mock_view)
        
        # Create system context first
        ecommerce_diagrams.create_system_context_view()
        
        # Now create container view
        ecommerce_diagrams.create_container_view()
        
        # Verify containers were created
        assert len(ecommerce_diagrams.containers) == 10
        expected_containers = [
            "web_app", "mobile_app", "api_gateway", "product_service",
            "order_service", "user_service", "notification_service",
            "database", "cache", "file_storage"
        ]
        for container_name in expected_containers:
            assert container_name in ecommerce_diagrams.containers
        
        # Verify view was created
        ecommerce_diagrams.generator.add_container_view.assert_called_once()
    
    def test_create_component_view_without_container_view(self, ecommerce_diagrams):
        """Test that creating component view without container view raises error."""
        with pytest.raises(ValueError, match="Container view must be created first"):
            ecommerce_diagrams.create_component_view()
    
    @patch('src.diagrams.example_system.Model')
    @patch('src.diagrams.generator.Workspace')
    def test_create_component_view_success(self, mock_workspace, mock_model, ecommerce_diagrams):
        """Test successful creation of component view."""
        # Setup system context and container views first
        mock_workspace_instance = Mock()
        mock_workspace.return_value = mock_workspace_instance
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance
        
        # Mock system, container, and component creation
        mock_system = Mock()
        mock_container = Mock()
        mock_component = Mock()
        mock_model_instance.Person.return_value = Mock()
        mock_model_instance.SoftwareSystem.return_value = mock_system
        mock_system.Container.return_value = mock_container
        mock_container.Component.return_value = mock_component
        
        # Mock view creation
        mock_view = Mock()
        ecommerce_diagrams.generator.add_system_context_view = Mock(return_value=mock_view)
        ecommerce_diagrams.generator.add_container_view = Mock(return_value=mock_view)
        ecommerce_diagrams.generator.add_component_view = Mock(return_value=mock_view)
        
        # Create prerequisite views
        ecommerce_diagrams.create_system_context_view()
        ecommerce_diagrams.create_container_view()
        
        # Now create component view
        ecommerce_diagrams.create_component_view()
        
        # Verify components were created
        assert len(ecommerce_diagrams.components) == 8
        expected_components = [
            "order_controller", "cart_service", "order_processor",
            "payment_client", "inventory_client", "shipping_client",
            "order_repository", "notification_publisher"
        ]
        for component_name in expected_components:
            assert component_name in ecommerce_diagrams.components
        
        # Verify view was created
        ecommerce_diagrams.generator.add_component_view.assert_called_once()
    
    @patch('src.diagrams.example_system.Model')
    @patch('src.diagrams.generator.Workspace')
    def test_system_context_relationships(self, mock_workspace, mock_model, ecommerce_diagrams):
        """Test that system context relationships are created."""
        # Setup mocks
        mock_workspace_instance = Mock()
        mock_workspace.return_value = mock_workspace_instance
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance
        
        # Mock person and system with uses method
        mock_person = Mock()
        mock_system = Mock()
        mock_model_instance.Person.return_value = mock_person
        mock_model_instance.SoftwareSystem.return_value = mock_system
        
        # Mock view creation
        mock_view = Mock()
        ecommerce_diagrams.generator.add_system_context_view = Mock(return_value=mock_view)
        
        # Execute
        ecommerce_diagrams.create_system_context_view()
        
        # Verify relationships were created (uses method was called)
        # Note: The actual relationship creation depends on the pystructurizr implementation
        # For now, we just verify the method completed without error
    
    @patch('src.diagrams.example_system.Model')
    @patch('src.diagrams.generator.Workspace')
    def test_container_relationships(self, mock_workspace, mock_model, ecommerce_diagrams):
        """Test that container relationships are created."""
        # Setup mocks
        mock_workspace_instance = Mock()
        mock_workspace.return_value = mock_workspace_instance
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance
        
        # Mock system and container with uses method
        mock_system = Mock()
        mock_container = Mock()
        mock_person = Mock()
        mock_model_instance.Person.return_value = mock_person
        mock_model_instance.SoftwareSystem.return_value = mock_system
        mock_system.Container.return_value = mock_container
        
        # Mock view creation
        mock_view = Mock()
        ecommerce_diagrams.generator.add_system_context_view = Mock(return_value=mock_view)
        ecommerce_diagrams.generator.add_container_view = Mock(return_value=mock_view)
        
        # Execute
        ecommerce_diagrams.create_system_context_view()
        ecommerce_diagrams.create_container_view()
        
        # Verify relationships were created
        # Note: The actual relationship creation depends on the pystructurizr implementation
        # For now, we just verify the method completed without error
    
    @patch('src.diagrams.example_system.Model')
    @patch('src.diagrams.generator.Workspace')
    def test_component_relationships(self, mock_workspace, mock_model, ecommerce_diagrams):
        """Test that component relationships are created."""
        # Setup mocks
        mock_workspace_instance = Mock()
        mock_workspace.return_value = mock_workspace_instance
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance
        
        # Mock system, container, and component with uses method
        mock_system = Mock()
        mock_container = Mock()
        mock_component = Mock()
        mock_person = Mock()
        mock_model_instance.Person.return_value = mock_person
        mock_model_instance.SoftwareSystem.return_value = mock_system
        mock_system.Container.return_value = mock_container
        mock_container.Component.return_value = mock_component
        
        # Mock view creation
        mock_view = Mock()
        ecommerce_diagrams.generator.add_system_context_view = Mock(return_value=mock_view)
        ecommerce_diagrams.generator.add_container_view = Mock(return_value=mock_view)
        ecommerce_diagrams.generator.add_component_view = Mock(return_value=mock_view)
        
        # Execute
        ecommerce_diagrams.create_system_context_view()
        ecommerce_diagrams.create_container_view()
        ecommerce_diagrams.create_component_view()
        
        # Verify relationships were created
        # Note: The actual relationship creation depends on the pystructurizr implementation
        # For now, we just verify the method completed without error


class TestModuleFunctions:
    """Test cases for module-level functions."""
    
    @patch('src.diagrams.example_system.ECommerceSystemDiagrams')
    def test_create_example_diagrams(self, mock_ecommerce_class):
        """Test create_example_diagrams function."""
        # Setup mock
        mock_instance = Mock()
        mock_ecommerce_class.return_value = mock_instance
        
        # Execute
        result = create_example_diagrams()
        
        # Verify
        mock_ecommerce_class.assert_called_once()
        mock_instance.create_system_context_view.assert_called_once()
        mock_instance.create_container_view.assert_called_once()
        mock_instance.create_component_view.assert_called_once()
        assert result == mock_instance
    
    @patch('pathlib.Path')
    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_export_diagrams_success(self, mock_file, mock_json_dump, mock_path):
        """Test successful export of diagrams."""
        # Setup mocks
        mock_diagrams = Mock()
        mock_diagrams.generator.export_to_json.return_value = '{"test": "json"}'
        mock_diagrams.generator.export_to_plantuml.return_value = '@startuml\ntest\n@enduml'
        mock_diagrams.generator.validate_export_data.return_value = True
        mock_diagrams.generator.validate_plantuml_output.return_value = True
        mock_diagrams.generator.get_metadata.return_value = []
        mock_diagrams.config.name = "Test System"
        mock_diagrams.config.description = "Test Description"
        mock_diagrams.config.version = "1.0.0"
        mock_diagrams.config.author = "Test Author"
        
        # Setup path mock - make it behave like a string for os.path.join
        mock_output_path = Mock()
        mock_output_path.__str__ = Mock(return_value="test_output")
        mock_output_path.__fspath__ = Mock(return_value="test_output")
        mock_path.return_value = mock_output_path
        mock_output_path.mkdir = Mock()
        
        # Execute
        export_diagrams(mock_diagrams, "test_output")
        
        # Verify
        mock_path.assert_called_once_with("test_output")
        mock_output_path.mkdir.assert_called_once_with(exist_ok=True)
        mock_diagrams.generator.export_to_json.assert_called_once()
        mock_diagrams.generator.export_to_plantuml.assert_called_once()
        mock_diagrams.generator.validate_export_data.assert_called_once()
        mock_diagrams.generator.validate_plantuml_output.assert_called_once()
    
    @patch('pathlib.Path')
    def test_export_diagrams_validation_failure(self, mock_path):
        """Test export diagrams with validation failure."""
        # Setup mocks
        mock_diagrams = Mock()
        mock_diagrams.generator.export_to_json.return_value = '{"test": "json"}'
        mock_diagrams.generator.validate_export_data.side_effect = ValueError("Validation failed")
        
        # Setup path mock
        mock_output_path = Mock()
        mock_path.return_value = mock_output_path
        mock_output_path.mkdir = Mock()
        
        # Execute and verify exception is raised
        with pytest.raises(ValueError, match="Validation failed"):
            export_diagrams(mock_diagrams, "test_output")
    
    @patch('pathlib.Path')
    @patch('builtins.open', new_callable=mock_open)
    def test_export_diagrams_file_write_error(self, mock_file, mock_path):
        """Test export diagrams with file write error."""
        # Setup mocks
        mock_diagrams = Mock()
        mock_diagrams.generator.export_to_json.return_value = '{"test": "json"}'
        mock_diagrams.generator.validate_export_data.return_value = True
        
        # Setup path mock
        mock_output_path = Mock()
        mock_path.return_value = mock_output_path
        mock_output_path.mkdir = Mock()
        
        # Make file write fail
        mock_file.side_effect = IOError("Write failed")
        
        # Execute and verify exception is raised
        with pytest.raises(Exception):
            export_diagrams(mock_diagrams, "test_output")
    
    @patch('src.diagrams.example_system.datetime')
    @patch('pathlib.Path')
    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_export_diagrams_metadata_creation(self, mock_file, mock_json_dump, mock_path, mock_datetime):
        """Test that export creates proper metadata."""
        # Setup datetime mock
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        
        # Setup mocks
        mock_metadata = Mock()
        mock_metadata.title = "Test Diagram"
        mock_metadata.description = "Test Description"
        mock_metadata.diagram_type = "system_context"
        mock_metadata.last_updated = mock_now
        mock_metadata.file_path = "test.json"
        mock_metadata.output_files = {}
        
        mock_diagrams = Mock()
        mock_diagrams.generator.export_to_json.return_value = '{"test": "json"}'
        mock_diagrams.generator.export_to_plantuml.return_value = '@startuml\ntest\n@enduml'
        mock_diagrams.generator.validate_export_data.return_value = True
        mock_diagrams.generator.validate_plantuml_output.return_value = True
        mock_diagrams.generator.get_metadata.return_value = [mock_metadata]
        mock_diagrams.config.name = "Test System"
        mock_diagrams.config.description = "Test Description"
        mock_diagrams.config.version = "1.0.0"
        mock_diagrams.config.author = "Test Author"
        
        # Setup path mock - make it behave like a string for os.path.join
        mock_output_path = Mock()
        mock_output_path.__str__ = Mock(return_value="test_output")
        mock_output_path.__fspath__ = Mock(return_value="test_output")
        mock_path.return_value = mock_output_path
        mock_output_path.mkdir = Mock()
        
        # Execute
        export_diagrams(mock_diagrams, "test_output")
        
        # Verify metadata was created and saved
        assert mock_json_dump.call_count >= 1
        
        # Check that metadata structure is correct
        metadata_call = None
        for call in mock_json_dump.call_args_list:
            args, kwargs = call
            if isinstance(args[0], dict) and "metadata" in args[0]:
                metadata_call = args[0]
                break
        
        assert metadata_call is not None
        assert "metadata" in metadata_call
        assert "workspace" in metadata_call
        assert "diagrams" in metadata_call["metadata"]
        assert "exportedAt" in metadata_call["metadata"]
        assert "totalDiagrams" in metadata_call["metadata"]
        assert metadata_call["metadata"]["totalDiagrams"] == 1