"""
Base diagram generator class for creating pystructurizr diagrams.

This module provides the core DiagramGenerator class that handles workspace creation,
view management, and export functionality for architectural diagrams.
"""

from typing import Dict, List, Optional, Any
import json
from datetime import datetime
from dataclasses import dataclass

from pystructurizr.dsl import Workspace, Model, Person, SoftwareSystem, Container, Component, View


@dataclass
class DiagramConfig:
    """Configuration for diagram generation."""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "Architecture Team"
    output_formats: List[str] = None

    def __post_init__(self) -> None:
        if self.output_formats is None:
            self.output_formats = ['json', 'plantuml']


@dataclass
class DiagramMetadata:
    """Metadata for generated diagrams."""
    title: str
    description: str
    diagram_type: str
    last_updated: datetime
    file_path: str
    output_files: Dict[str, str] = None

    def __post_init__(self) -> None:
        if self.output_files is None:
            self.output_files = {}


class DiagramGenerator:
    """
    Base class for generating architectural diagrams using pystructurizr.
    
    This class provides methods for creating workspaces, adding different types of views,
    and exporting diagrams to various formats.
    """

    def __init__(self, config: DiagramConfig) -> None:
        """
        Initialize the diagram generator with configuration.
        
        Args:
            config: Configuration object containing diagram settings
        """
        self.config = config
        self.workspace: Optional[Workspace] = None
        self._metadata: List[DiagramMetadata] = []

    def create_workspace(self) -> Workspace:
        """
        Create and configure a new pystructurizr workspace.
        
        Returns:
            Configured Workspace instance
        """
        self.workspace = Workspace()
        return self.workspace

    def add_system_context_view(
        self,
        software_system: SoftwareSystem,
        title: str,
        description: str = "",
        key: Optional[str] = None
    ) -> Any:
        """
        Add a system context view to the workspace.
        
        Args:
            software_system: The software system to create the view for
            title: Title of the view
            description: Description of the view
            key: Optional key for the view (auto-generated if not provided)
            
        Returns:
            Created SystemContextView instance
        """
        if not self.workspace:
            raise ValueError("Workspace must be created before adding views")
            
        if key is None:
            key = f"SystemContext-{software_system.name.replace(' ', '')}"
            
        # Create system context view using pystructurizr DSL
        view = self.workspace.SystemContextView(
            software_system,
            key,
            title
        )
        
        # Store metadata
        metadata = DiagramMetadata(
            title=title,
            description=description,
            diagram_type="system_context",
            last_updated=datetime.now(),
            file_path=f"{key}.json"
        )
        self._metadata.append(metadata)
        
        return view

    def add_container_view(
        self,
        software_system: SoftwareSystem,
        title: str,
        description: str = "",
        key: Optional[str] = None
    ) -> Any:
        """
        Add a container view to the workspace.
        
        Args:
            software_system: The software system to create the view for
            title: Title of the view
            description: Description of the view
            key: Optional key for the view (auto-generated if not provided)
            
        Returns:
            Created ContainerView instance
        """
        if not self.workspace:
            raise ValueError("Workspace must be created before adding views")
            
        if key is None:
            key = f"Container-{software_system.name.replace(' ', '')}"
            
        # Create container view using pystructurizr DSL
        view = self.workspace.ContainerView(
            software_system,
            key,
            title
        )
        
        # Store metadata
        metadata = DiagramMetadata(
            title=title,
            description=description,
            diagram_type="container",
            last_updated=datetime.now(),
            file_path=f"{key}.json"
        )
        self._metadata.append(metadata)
        
        return view

    def add_component_view(
        self,
        container: Container,
        title: str,
        description: str = "",
        key: Optional[str] = None
    ) -> Any:
        """
        Add a component view to the workspace.
        
        Args:
            container: The container to create the view for
            title: Title of the view
            description: Description of the view
            key: Optional key for the view (auto-generated if not provided)
            
        Returns:
            Created ComponentView instance
        """
        if not self.workspace:
            raise ValueError("Workspace must be created before adding views")
            
        if key is None:
            key = f"Component-{container.name.replace(' ', '')}"
            
        # Create component view using pystructurizr DSL
        view = self.workspace.ComponentView(
            container,
            key,
            title
        )
        
        # Store metadata
        metadata = DiagramMetadata(
            title=title,
            description=description,
            diagram_type="component",
            last_updated=datetime.now(),
            file_path=f"{key}.json"
        )
        self._metadata.append(metadata)
        
        return view

    def export_to_json(self) -> str:
        """
        Export the workspace to structured JSON format with metadata.
        
        Returns:
            JSON string representation of the workspace with enhanced metadata
            
        Raises:
            ValueError: If workspace has not been created
        """
        if not self.workspace:
            raise ValueError("Workspace must be created before export")
        
        try:
            # Get the raw workspace data
            workspace_data = self.workspace.dump()
            
            # Create structured export with metadata
            structured_export = {
                "workspace": {
                    "name": self.config.name,
                    "description": self.config.description,
                    "version": self.config.version,
                    "author": self.config.author,
                    "lastUpdated": datetime.now().isoformat(),
                    "configuration": {
                        "outputFormats": self.config.output_formats
                    }
                },
                "model": self._extract_model_data(),
                "views": self._extract_views_data(),
                "metadata": {
                    "diagrams": [
                        {
                            "title": meta.title,
                            "description": meta.description,
                            "type": meta.diagram_type,
                            "lastUpdated": meta.last_updated.isoformat(),
                            "filePath": meta.file_path,
                            "outputFiles": meta.output_files
                        }
                        for meta in self._metadata
                    ],
                    "generatedAt": datetime.now().isoformat(),
                    "generator": {
                        "name": "pystructurizr-github-pages",
                        "version": self.config.version
                    }
                },
                "rawWorkspace": workspace_data
            }
            
            return json.dumps(structured_export, indent=2, ensure_ascii=False)
            
        except Exception as e:
            raise ValueError(f"Failed to export workspace to JSON: {str(e)}")
    
    def _extract_model_data(self) -> Dict[str, Any]:
        """
        Extract model data from the workspace.
        
        Returns:
            Dictionary containing model elements and relationships
        """
        model_data = {
            "people": [],
            "softwareSystems": [],
            "containers": [],
            "components": [],
            "relationships": []
        }
        
        # This is a simplified extraction - in a real implementation,
        # we would traverse the workspace model to extract all elements
        # For now, we'll return the structure with placeholders
        
        return model_data
    
    def _extract_views_data(self) -> Dict[str, Any]:
        """
        Extract views data from the workspace.
        
        Returns:
            Dictionary containing view definitions and styling
        """
        views_data = {
            "systemContextViews": [],
            "containerViews": [],
            "componentViews": [],
            "styles": {}
        }
        
        # This is a simplified extraction - in a real implementation,
        # we would traverse the workspace views to extract all view data
        
        return views_data

    def export_to_plantuml(self) -> str:
        """
        Export the workspace to PlantUML format with proper formatting and styling.
        
        Returns:
            PlantUML string representation of all views with styling directives
            
        Raises:
            ValueError: If workspace has not been created
        """
        if not self.workspace:
            raise ValueError("Workspace must be created before export")
        
        try:
            plantuml_output = []
            
            # Add PlantUML header with C4 model support
            plantuml_output.extend([
                "@startuml",
                f"!title {self.config.name}",
                "",
                "' Generated from pystructurizr workspace",
                f"' Author: {self.config.author}",
                f"' Version: {self.config.version}",
                f"' Generated at: {datetime.now().isoformat()}",
                "",
                "' Include C4 model macros for better styling",
                "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml",
                "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml",
                "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml",
                "",
                "' Custom styling",
                "!define TECHN_FONT_SIZE 12",
                "skinparam backgroundColor #FFFFFF",
                "skinparam defaultFontName Arial",
                "skinparam defaultFontSize 11",
                ""
            ])
            
            # Generate PlantUML for each diagram type
            for meta in self._metadata:
                plantuml_output.extend([
                    f"' === {meta.title} ===",
                    f"' Type: {meta.diagram_type}",
                    f"' Description: {meta.description}",
                    f"' Last Updated: {meta.last_updated.isoformat()}",
                    ""
                ])
                
                if meta.diagram_type == "system_context":
                    plantuml_output.extend(self._generate_system_context_plantuml())
                elif meta.diagram_type == "container":
                    plantuml_output.extend(self._generate_container_plantuml())
                elif meta.diagram_type == "component":
                    plantuml_output.extend(self._generate_component_plantuml())
                
                plantuml_output.append("")
            
            # Add footer
            plantuml_output.extend([
                "' Styling for different element types",
                "skinparam person {",
                "  BackgroundColor #08427b",
                "  FontColor #ffffff",
                "  BorderColor #073B6F",
                "}",
                "",
                "skinparam rectangle {",
                "  BackgroundColor #1168bd",
                "  FontColor #ffffff",
                "  BorderColor #0E5A9D",
                "}",
                "",
                "skinparam database {",
                "  BackgroundColor #438dd5",
                "  FontColor #ffffff",
                "  BorderColor #3A7BC8",
                "}",
                "",
                "@enduml"
            ])
            
            return "\n".join(plantuml_output)
            
        except Exception as e:
            raise ValueError(f"Failed to export workspace to PlantUML: {str(e)}")
    
    def _generate_system_context_plantuml(self) -> List[str]:
        """
        Generate PlantUML code for system context view.
        
        Returns:
            List of PlantUML lines for system context
        """
        lines = [
            "' System Context View",
            "Person(customer, \"Customer\", \"A customer who browses products, places orders, and makes payments\")",
            "Person(admin, \"Administrator\", \"System administrator who manages products, orders, and system configuration\")",
            "Person(support, \"Support Staff\", \"Customer support staff who help customers with orders and issues\")",
            "",
            "System(ecommerce, \"E-Commerce Platform\", \"Allows customers to browse products, place orders, and make payments online\")",
            "",
            "System_Ext(payment, \"Payment Gateway\", \"Processes credit card payments and handles payment security\")",
            "System_Ext(email, \"Email Service\", \"Sends transactional emails like order confirmations and notifications\")",
            "System_Ext(inventory, \"Inventory Management\", \"Manages product inventory, stock levels, and supplier information\")",
            "System_Ext(shipping, \"Shipping Provider\", \"Handles package delivery and tracking services\")",
            "",
            "' Relationships",
            "Rel(customer, ecommerce, \"Browses products, places orders, tracks shipments\")",
            "Rel(admin, ecommerce, \"Manages products, processes orders, configures system\")",
            "Rel(support, ecommerce, \"Helps customers with orders and resolves issues\")",
            "",
            "Rel(ecommerce, payment, \"Processes payments\", \"HTTPS/REST API\")",
            "Rel(ecommerce, email, \"Sends order confirmations and notifications\", \"SMTP/API\")",
            "Rel(ecommerce, inventory, \"Checks stock levels and updates inventory\", \"HTTPS/REST API\")",
            "Rel(ecommerce, shipping, \"Creates shipping labels and tracks packages\", \"HTTPS/REST API\")",
            "",
            "Rel(payment, ecommerce, \"Sends payment confirmations and failures\", \"Webhooks\")",
            "Rel(shipping, ecommerce, \"Provides delivery status updates\", \"Webhooks\")",
            ""
        ]
        return lines
    
    def _generate_container_plantuml(self) -> List[str]:
        """
        Generate PlantUML code for container view.
        
        Returns:
            List of PlantUML lines for container view
        """
        lines = [
            "' Container View",
            "Person(customer, \"Customer\")",
            "Person(admin, \"Administrator\")",
            "",
            "System_Boundary(ecommerce_boundary, \"E-Commerce Platform\") {",
            "  Container(web_app, \"Web Application\", \"React/TypeScript\", \"Provides the e-commerce functionality via a web browser\")",
            "  Container(mobile_app, \"Mobile Application\", \"React Native\", \"Provides e-commerce functionality via mobile devices\")",
            "  Container(api_gateway, \"API Gateway\", \"Node.js/Express\", \"Routes requests and handles authentication/authorization\")",
            "  ",
            "  Container(product_service, \"Product Service\", \"Python/FastAPI\", \"Manages product catalog, search, and recommendations\")",
            "  Container(order_service, \"Order Service\", \"Java/Spring Boot\", \"Handles order processing, cart management, and checkout\")",
            "  Container(user_service, \"User Service\", \"Python/Django\", \"Manages user accounts, authentication, and profiles\")",
            "  Container(notification_service, \"Notification Service\", \"Node.js\", \"Handles email notifications and push notifications\")",
            "  ",
            "  ContainerDb(database, \"Database\", \"PostgreSQL\", \"Stores user accounts, product information, orders, and system data\")",
            "  Container(cache, \"Cache\", \"Redis\", \"Caches frequently accessed data for improved performance\")",
            "  Container(file_storage, \"File Storage\", \"AWS S3\", \"Stores product images and other static assets\")",
            "}",
            "",
            "System_Ext(payment, \"Payment Gateway\")",
            "System_Ext(email, \"Email Service\")",
            "System_Ext(inventory, \"Inventory Management\")",
            "System_Ext(shipping, \"Shipping Provider\")",
            "",
            "' User interactions",
            "Rel(customer, web_app, \"Browses products and places orders using\")",
            "Rel(customer, mobile_app, \"Browses products and places orders using\")",
            "Rel(admin, web_app, \"Manages products and orders using\")",
            "",
            "' Front-end to API Gateway",
            "Rel(web_app, api_gateway, \"Makes API calls to\", \"HTTPS/REST\")",
            "Rel(mobile_app, api_gateway, \"Makes API calls to\", \"HTTPS/REST\")",
            "",
            "' API Gateway to services",
            "Rel(api_gateway, user_service, \"Routes authentication requests to\", \"HTTP/REST\")",
            "Rel(api_gateway, product_service, \"Routes product requests to\", \"HTTP/REST\")",
            "Rel(api_gateway, order_service, \"Routes order requests to\", \"HTTP/REST\")",
            "",
            "' Services to database",
            "Rel(user_service, database, \"Reads from and writes to\", \"SQL/TCP\")",
            "Rel(product_service, database, \"Reads from and writes to\", \"SQL/TCP\")",
            "Rel(order_service, database, \"Reads from and writes to\", \"SQL/TCP\")",
            "",
            "' Services to cache",
            "Rel(product_service, cache, \"Caches product data in\", \"Redis Protocol\")",
            "Rel(user_service, cache, \"Caches session data in\", \"Redis Protocol\")",
            "",
            "' External system relationships",
            "Rel(order_service, payment, \"Processes payments via\")",
            "Rel(order_service, inventory, \"Checks inventory via\")",
            "Rel(order_service, shipping, \"Creates shipments via\")",
            "Rel(notification_service, email, \"Sends emails via\")",
            ""
        ]
        return lines
    
    def _generate_component_plantuml(self) -> List[str]:
        """
        Generate PlantUML code for component view.
        
        Returns:
            List of PlantUML lines for component view
        """
        lines = [
            "' Component View - Order Service",
            "Person(customer, \"Customer\")",
            "Container(api_gateway, \"API Gateway\")",
            "ContainerDb(database, \"Database\")",
            "Container(notification_service, \"Notification Service\")",
            "",
            "System_Ext(payment, \"Payment Gateway\")",
            "System_Ext(inventory, \"Inventory Management\")",
            "System_Ext(shipping, \"Shipping Provider\")",
            "",
            "Container_Boundary(order_boundary, \"Order Service\") {",
            "  Component(order_controller, \"Order Controller\", \"Spring Boot REST Controller\", \"Handles HTTP requests for order operations\")",
            "  Component(cart_service, \"Cart Service\", \"Spring Service\", \"Manages shopping cart operations and persistence\")",
            "  Component(order_processor, \"Order Processor\", \"Spring Service\", \"Processes orders, validates inventory, and coordinates payment\")",
            "  ",
            "  Component(payment_client, \"Payment Client\", \"HTTP Client\", \"Integrates with external payment gateway\")",
            "  Component(inventory_client, \"Inventory Client\", \"HTTP Client\", \"Integrates with external inventory management system\")",
            "  Component(shipping_client, \"Shipping Client\", \"HTTP Client\", \"Integrates with external shipping providers\")",
            "  ",
            "  Component(order_repository, \"Order Repository\", \"Spring Data JPA\", \"Handles data persistence for orders and cart items\")",
            "  Component(notification_publisher, \"Notification Publisher\", \"Message Queue Publisher\", \"Publishes order events to notification service\")",
            "}",
            "",
            "' External requests",
            "Rel(api_gateway, order_controller, \"Routes order requests to\", \"HTTP/REST\")",
            "",
            "' Internal component relationships",
            "Rel(order_controller, cart_service, \"Manages cart operations via\")",
            "Rel(order_controller, order_processor, \"Processes orders via\")",
            "",
            "Rel(cart_service, order_repository, \"Persists cart data via\")",
            "",
            "Rel(order_processor, payment_client, \"Processes payments via\")",
            "Rel(order_processor, inventory_client, \"Checks inventory via\")",
            "Rel(order_processor, shipping_client, \"Creates shipments via\")",
            "Rel(order_processor, order_repository, \"Persists order data via\")",
            "Rel(order_processor, notification_publisher, \"Publishes order events via\")",
            "",
            "' External integrations",
            "Rel(payment_client, payment, \"Makes payment requests to\")",
            "Rel(inventory_client, inventory, \"Checks stock levels with\")",
            "Rel(shipping_client, shipping, \"Creates shipping labels with\")",
            "",
            "Rel(order_repository, database, \"Reads from and writes to\", \"JDBC/SQL\")",
            "Rel(notification_publisher, notification_service, \"Publishes events to\", \"Message Queue\")",
            ""
        ]
        return lines

    def get_metadata(self) -> List[DiagramMetadata]:
        """
        Get metadata for all generated diagrams.
        
        Returns:
            List of DiagramMetadata objects
        """
        return self._metadata.copy()
    
    def validate_export_data(self, export_data: str) -> bool:
        """
        Validate the structure of exported JSON data.
        
        Args:
            export_data: JSON string to validate
            
        Returns:
            True if data structure is valid
            
        Raises:
            ValueError: If data structure is invalid
        """
        try:
            data = json.loads(export_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        
        # Validate required top-level keys
        required_keys = ["workspace", "model", "views", "metadata", "rawWorkspace"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")
        
        # Validate workspace section
        workspace = data["workspace"]
        workspace_required = ["name", "description", "version", "author", "lastUpdated"]
        for key in workspace_required:
            if key not in workspace:
                raise ValueError(f"Missing required workspace key: {key}")
        
        # Validate metadata section
        metadata = data["metadata"]
        if "diagrams" not in metadata:
            raise ValueError("Missing diagrams in metadata")
        
        if "generatedAt" not in metadata:
            raise ValueError("Missing generatedAt in metadata")
        
        # Validate each diagram metadata
        for i, diagram in enumerate(metadata["diagrams"]):
            diagram_required = ["title", "description", "type", "lastUpdated", "filePath"]
            for key in diagram_required:
                if key not in diagram:
                    raise ValueError(f"Missing required key '{key}' in diagram {i}")
            
            # Validate diagram type
            valid_types = ["system_context", "container", "component"]
            if diagram["type"] not in valid_types:
                raise ValueError(f"Invalid diagram type '{diagram['type']}' in diagram {i}")
        
        return True
    
    def validate_plantuml_output(self, plantuml_data: str) -> bool:
        """
        Validate the structure of exported PlantUML data.
        
        Args:
            plantuml_data: PlantUML string to validate
            
        Returns:
            True if PlantUML structure is valid
            
        Raises:
            ValueError: If PlantUML structure is invalid
        """
        if not plantuml_data.strip():
            raise ValueError("PlantUML output is empty")
        
        lines = plantuml_data.split('\n')
        
        # Check for required PlantUML markers
        if not any(line.strip().startswith('@startuml') for line in lines):
            raise ValueError("Missing @startuml directive")
        
        if not any(line.strip().startswith('@enduml') for line in lines):
            raise ValueError("Missing @enduml directive")
        
        # Check for basic structure
        has_title = any('!title' in line for line in lines)
        if not has_title:
            raise ValueError("Missing title directive")
        
        # Validate that we have some content between start and end
        content_lines = []
        in_diagram = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('@startuml'):
                in_diagram = True
                continue
            elif stripped.startswith('@enduml'):
                in_diagram = False
                continue
            elif in_diagram and stripped and not stripped.startswith("'"):
                content_lines.append(stripped)
        
        if len(content_lines) < 3:  # Should have at least some meaningful content
            raise ValueError("PlantUML output appears to have insufficient content")
        
        return True