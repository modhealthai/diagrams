"""
Example system architecture diagrams using pystructurizr.

This module demonstrates how to create comprehensive architectural diagrams
including system context, container, and component views for a sample
e-commerce system.

The example includes:
- System Context View: Shows the e-commerce platform and its interactions with users and external systems
- Container View: Shows the internal structure of the e-commerce platform with different containers/services
- Component View: Shows the detailed internal structure of the Order Service container

This serves as a complete example of how to use pystructurizr to document
software architecture at different levels of detail.
"""

from typing import Dict, Any
from datetime import datetime

from pystructurizr.dsl import Workspace, Model, Person, SoftwareSystem, Container, Component

try:
    from .generator import DiagramGenerator, DiagramConfig
    from .utils import ElementFactory, RelationshipManager, ViewStyler
except ImportError:
    # Handle running as script or in different contexts
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    from generator import DiagramGenerator, DiagramConfig
    from utils import ElementFactory, RelationshipManager, ViewStyler


class ECommerceSystemDiagrams:
    """
    Example implementation of architectural diagrams for an e-commerce system.
    
    This class demonstrates best practices for creating system context,
    container, and component views using pystructurizr.
    """
    
    def __init__(self) -> None:
        """Initialize the e-commerce system diagram generator."""
        self.config = DiagramConfig(
            name="E-Commerce System Architecture",
            description="Comprehensive architectural documentation for an e-commerce platform",
            version="1.0.0",
            author="Architecture Team",
            output_formats=["json", "plantuml"]
        )
        
        self.generator = DiagramGenerator(self.config)
        self.workspace: Workspace = None
        self.model: Model = None
        
        # Store references to key elements
        self.people: Dict[str, Person] = {}
        self.systems: Dict[str, SoftwareSystem] = {}
        self.containers: Dict[str, Container] = {}
        self.components: Dict[str, Component] = {}
    
    def create_system_context_view(self) -> None:
        """
        Create a comprehensive system context view showing the e-commerce system
        and its interactions with users and external systems.
        """
        # Create workspace and model
        self.workspace = self.generator.create_workspace()
        
        # Create model - the Model method returns a string identifier, not a model object
        # We need to create the model directly
        from pystructurizr.dsl import Model
        self.model = Model("ECommerceModel")
        
        # Define people (actors)
        self.people["customer"] = self.model.Person(
            "Customer",
            "A customer who browses products, places orders, and makes payments"
        )
        
        self.people["admin"] = self.model.Person(
            "Administrator", 
            "System administrator who manages products, orders, and system configuration"
        )
        
        self.people["support"] = self.model.Person(
            "Support Staff",
            "Customer support staff who help customers with orders and issues"
        )
        
        # Define the main software system
        self.systems["ecommerce"] = self.model.SoftwareSystem(
            "E-Commerce Platform",
            "Allows customers to browse products, place orders, and make payments online"
        )
        
        # Define external systems
        self.systems["payment"] = self.model.SoftwareSystem(
            "Payment Gateway",
            "Processes credit card payments and handles payment security"
        )
        
        self.systems["email"] = self.model.SoftwareSystem(
            "Email Service",
            "Sends transactional emails like order confirmations and notifications"
        )
        
        self.systems["inventory"] = self.model.SoftwareSystem(
            "Inventory Management",
            "Manages product inventory, stock levels, and supplier information"
        )
        
        self.systems["shipping"] = self.model.SoftwareSystem(
            "Shipping Provider",
            "Handles package delivery and tracking services"
        )
        
        # Define relationships
        self._add_system_context_relationships()
        
        # Create the system context view using the generator method
        system_context_view = self.generator.add_system_context_view(
            self.systems["ecommerce"],
            "E-Commerce System - System Context",
            "Shows the e-commerce platform and its interactions with users and external systems",
            "SystemContext"
        )
        
        # Add all people and systems to the view
        for person in self.people.values():
            system_context_view.include(person)
        for system in self.systems.values():
            system_context_view.include(system)
        
        # Apply styling
        ViewStyler.apply_custom_theme(system_context_view, "corporate")
        
        print("✓ System context view created successfully")
    
    def _add_system_context_relationships(self) -> None:
        """Add relationships for the system context view."""
        # Customer relationships
        self.people["customer"].uses(
            self.systems["ecommerce"],
            "Browses products, places orders, tracks shipments"
        )
        
        # Administrator relationships
        self.people["admin"].uses(
            self.systems["ecommerce"],
            "Manages products, processes orders, configures system"
        )
        
        # Support staff relationships
        self.people["support"].uses(
            self.systems["ecommerce"],
            "Helps customers with orders and resolves issues"
        )
        
        # System-to-system relationships
        self.systems["ecommerce"].uses(
            self.systems["payment"],
            "Processes payments",
            "HTTPS/REST API"
        )
        
        self.systems["ecommerce"].uses(
            self.systems["email"],
            "Sends order confirmations and notifications",
            "SMTP/API"
        )
        
        self.systems["ecommerce"].uses(
            self.systems["inventory"],
            "Checks stock levels and updates inventory",
            "HTTPS/REST API"
        )
        
        self.systems["ecommerce"].uses(
            self.systems["shipping"],
            "Creates shipping labels and tracks packages",
            "HTTPS/REST API"
        )
        
        # External system notifications back to e-commerce
        self.systems["payment"].uses(
            self.systems["ecommerce"],
            "Sends payment confirmations and failures",
            "Webhooks"
        )
        
        self.systems["shipping"].uses(
            self.systems["ecommerce"],
            "Provides delivery status updates",
            "Webhooks"
        )
    
    def create_container_view(self) -> None:
        """
        Create a container view showing the internal structure of the e-commerce system.
        """
        if not self.workspace:
            raise ValueError("System context view must be created first")
        
        ecommerce_system = self.systems["ecommerce"]
        
        # Define containers within the e-commerce system
        self.containers["web_app"] = ecommerce_system.Container(
            "Web Application",
            "Provides the e-commerce functionality via a web browser",
            "React/TypeScript"
        )
        
        self.containers["mobile_app"] = ecommerce_system.Container(
            "Mobile Application", 
            "Provides e-commerce functionality via mobile devices",
            "React Native"
        )
        
        self.containers["api_gateway"] = ecommerce_system.Container(
            "API Gateway",
            "Routes requests and handles authentication/authorization",
            "Node.js/Express"
        )
        
        self.containers["product_service"] = ecommerce_system.Container(
            "Product Service",
            "Manages product catalog, search, and recommendations",
            "Python/FastAPI"
        )
        
        self.containers["order_service"] = ecommerce_system.Container(
            "Order Service",
            "Handles order processing, cart management, and checkout",
            "Java/Spring Boot"
        )
        
        self.containers["user_service"] = ecommerce_system.Container(
            "User Service",
            "Manages user accounts, authentication, and profiles",
            "Python/Django"
        )
        
        self.containers["notification_service"] = ecommerce_system.Container(
            "Notification Service",
            "Handles email notifications and push notifications",
            "Node.js"
        )
        
        self.containers["database"] = ecommerce_system.Container(
            "Database",
            "Stores user accounts, product information, orders, and system data",
            "PostgreSQL"
        )
        
        self.containers["cache"] = ecommerce_system.Container(
            "Cache",
            "Caches frequently accessed data for improved performance",
            "Redis"
        )
        
        self.containers["file_storage"] = ecommerce_system.Container(
            "File Storage",
            "Stores product images and other static assets",
            "AWS S3"
        )
        
        # Define container relationships
        self._add_container_relationships()
        
        # Create the container view using the generator method
        container_view = self.generator.add_container_view(
            ecommerce_system,
            "E-Commerce System - Container View",
            "Shows the internal structure of the e-commerce platform with different containers/services",
            "ContainerView"
        )
        
        # Add people and external systems to show context
        for person in self.people.values():
            container_view.include(person)
        for system in self.systems.values():
            container_view.include(system)
        
        # Apply styling
        ViewStyler.apply_custom_theme(container_view, "modern")
        
        print("✓ Container view created successfully")
    
    def create_component_view(self) -> None:
        """
        Create a component view showing the internal structure of the Order Service container.
        """
        if not self.workspace:
            raise ValueError("Container view must be created first")
        
        order_service = self.containers["order_service"]
        
        # Define components within the Order Service container
        self.components["order_controller"] = order_service.Component(
            "Order Controller",
            "Handles HTTP requests for order operations",
            "Spring Boot REST Controller"
        )
        
        self.components["cart_service"] = order_service.Component(
            "Cart Service",
            "Manages shopping cart operations and persistence",
            "Spring Service"
        )
        
        self.components["order_processor"] = order_service.Component(
            "Order Processor",
            "Processes orders, validates inventory, and coordinates payment",
            "Spring Service"
        )
        
        self.components["payment_client"] = order_service.Component(
            "Payment Client",
            "Integrates with external payment gateway",
            "HTTP Client"
        )
        
        self.components["inventory_client"] = order_service.Component(
            "Inventory Client",
            "Integrates with external inventory management system",
            "HTTP Client"
        )
        
        self.components["shipping_client"] = order_service.Component(
            "Shipping Client",
            "Integrates with external shipping providers",
            "HTTP Client"
        )
        
        self.components["order_repository"] = order_service.Component(
            "Order Repository",
            "Handles data persistence for orders and cart items",
            "Spring Data JPA"
        )
        
        self.components["notification_publisher"] = order_service.Component(
            "Notification Publisher",
            "Publishes order events to notification service",
            "Message Queue Publisher"
        )
        
        # Define component relationships
        self._add_component_relationships()
        
        # Create the component view using the generator method
        component_view = self.generator.add_component_view(
            order_service,
            "Order Service - Component View",
            "Shows the detailed internal structure of the Order Service container",
            "ComponentView"
        )
        
        # Add relevant external elements to show context
        component_view.include(self.people["customer"])
        component_view.include(self.containers["api_gateway"])
        component_view.include(self.containers["database"])
        component_view.include(self.containers["notification_service"])
        component_view.include(self.systems["payment"])
        component_view.include(self.systems["inventory"])
        component_view.include(self.systems["shipping"])
        
        # Apply styling
        ViewStyler.apply_custom_theme(component_view, "minimal")
        
        print("✓ Component view created successfully")
    
    def _add_component_relationships(self) -> None:
        """Add relationships for the component view."""
        # External requests to Order Controller
        self.containers["api_gateway"].uses(
            self.components["order_controller"],
            "Routes order requests to",
            "HTTP/REST"
        )
        
        # Order Controller to internal services
        self.components["order_controller"].uses(
            self.components["cart_service"],
            "Manages cart operations via"
        )
        
        self.components["order_controller"].uses(
            self.components["order_processor"],
            "Processes orders via"
        )
        
        # Cart Service relationships
        self.components["cart_service"].uses(
            self.components["order_repository"],
            "Persists cart data via"
        )
        
        # Order Processor relationships
        self.components["order_processor"].uses(
            self.components["payment_client"],
            "Processes payments via"
        )
        
        self.components["order_processor"].uses(
            self.components["inventory_client"],
            "Checks inventory via"
        )
        
        self.components["order_processor"].uses(
            self.components["shipping_client"],
            "Creates shipments via"
        )
        
        self.components["order_processor"].uses(
            self.components["order_repository"],
            "Persists order data via"
        )
        
        self.components["order_processor"].uses(
            self.components["notification_publisher"],
            "Publishes order events via"
        )
        
        # External client relationships
        self.components["payment_client"].uses(
            self.systems["payment"],
            "Makes payment requests to"
        )
        
        self.components["inventory_client"].uses(
            self.systems["inventory"],
            "Checks stock levels with"
        )
        
        self.components["shipping_client"].uses(
            self.systems["shipping"],
            "Creates shipping labels with"
        )
        
        # Repository to database
        self.components["order_repository"].uses(
            self.containers["database"],
            "Reads from and writes to",
            "JDBC/SQL"
        )
        
        # Notification publisher to notification service
        self.components["notification_publisher"].uses(
            self.containers["notification_service"],
            "Publishes events to",
            "Message Queue"
        )
    
    def _add_container_relationships(self) -> None:
        """Add relationships for the container view."""
        # User interactions with front-end applications
        self.people["customer"].uses(
            self.containers["web_app"],
            "Browses products and places orders using"
        )
        
        self.people["customer"].uses(
            self.containers["mobile_app"],
            "Browses products and places orders using"
        )
        
        self.people["admin"].uses(
            self.containers["web_app"],
            "Manages products and orders using"
        )
        
        # Front-end to API Gateway
        self.containers["web_app"].uses(
            self.containers["api_gateway"],
            "Makes API calls to",
            "HTTPS/REST"
        )
        
        self.containers["mobile_app"].uses(
            self.containers["api_gateway"],
            "Makes API calls to",
            "HTTPS/REST"
        )
        
        # API Gateway to services
        self.containers["api_gateway"].uses(
            self.containers["user_service"],
            "Routes authentication requests to",
            "HTTP/REST"
        )
        
        self.containers["api_gateway"].uses(
            self.containers["product_service"],
            "Routes product requests to",
            "HTTP/REST"
        )
        
        self.containers["api_gateway"].uses(
            self.containers["order_service"],
            "Routes order requests to",
            "HTTP/REST"
        )
        
        # Services to database
        self.containers["user_service"].uses(
            self.containers["database"],
            "Reads from and writes to",
            "SQL/TCP"
        )
        
        self.containers["product_service"].uses(
            self.containers["database"],
            "Reads from and writes to",
            "SQL/TCP"
        )
        
        self.containers["order_service"].uses(
            self.containers["database"],
            "Reads from and writes to",
            "SQL/TCP"
        )
        
        # Services to cache
        self.containers["product_service"].uses(
            self.containers["cache"],
            "Caches product data in",
            "Redis Protocol"
        )
        
        self.containers["user_service"].uses(
            self.containers["cache"],
            "Caches session data in",
            "Redis Protocol"
        )
        
        # File storage relationships
        self.containers["product_service"].uses(
            self.containers["file_storage"],
            "Stores and retrieves product images from",
            "HTTPS/S3 API"
        )
        
        # Notification service relationships
        self.containers["order_service"].uses(
            self.containers["notification_service"],
            "Sends order notifications via",
            "Message Queue"
        )
        
        self.containers["notification_service"].uses(
            self.systems["email"],
            "Sends emails via"
        )
        
        # External system relationships
        self.containers["order_service"].uses(
            self.systems["payment"],
            "Processes payments via"
        )
        
        self.containers["order_service"].uses(
            self.systems["inventory"],
            "Checks inventory via"
        )
        
        self.containers["order_service"].uses(
            self.systems["shipping"],
            "Creates shipments via"
        )


def create_example_diagrams() -> ECommerceSystemDiagrams:
    """
    Create and return a complete set of example diagrams.
    
    Returns:
        ECommerceSystemDiagrams instance with all views created
    """
    diagrams = ECommerceSystemDiagrams()
    
    print("Creating example e-commerce system diagrams...")
    print("=" * 50)
    
    # Create system context view
    print("1. Creating system context view...")
    diagrams.create_system_context_view()
    
    # Create container view
    print("2. Creating container view...")
    diagrams.create_container_view()
    
    # Create component view
    print("3. Creating component view...")
    diagrams.create_component_view()
    
    print("=" * 50)
    print("✓ All example diagrams created successfully!")
    
    return diagrams


def export_diagrams(diagrams: ECommerceSystemDiagrams, output_dir: str = "docs") -> None:
    """
    Export diagrams to JSON and PlantUML formats with enhanced metadata and validation.
    
    Args:
        diagrams: ECommerceSystemDiagrams instance
        output_dir: Directory to save exported files
    """
    import os
    from pathlib import Path
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print(f"Exporting diagrams to {output_dir}/...")
    
    try:
        # Export to JSON with enhanced metadata
        json_output = diagrams.generator.export_to_json()
        
        # Validate the exported data
        diagrams.generator.validate_export_data(json_output)
        print("✓ JSON export data validation passed")
        
        # Save JSON export
        json_file = output_path / "ecommerce_architecture.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"✓ Enhanced JSON export saved to {json_file}")
        
        # Export to PlantUML with validation
        plantuml_output = diagrams.generator.export_to_plantuml()
        
        # Validate the PlantUML output
        diagrams.generator.validate_plantuml_output(plantuml_output)
        print("✓ PlantUML export data validation passed")
        
        plantuml_file = output_path / "ecommerce_architecture.puml"
        with open(plantuml_file, 'w', encoding='utf-8') as f:
            f.write(plantuml_output)
        print(f"✓ Enhanced PlantUML export saved to {plantuml_file}")
        
        # Export enhanced metadata
        metadata = diagrams.generator.get_metadata()
        metadata_file = output_path / "diagram_metadata.json"
        
        import json
        enhanced_metadata = {
            "workspace": {
                "name": diagrams.config.name,
                "description": diagrams.config.description,
                "version": diagrams.config.version,
                "author": diagrams.config.author
            },
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
                    for meta in metadata
                ],
                "exportedAt": datetime.now().isoformat(),
                "totalDiagrams": len(metadata)
            }
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_metadata, f, indent=2, ensure_ascii=False)
        print(f"✓ Enhanced metadata saved to {metadata_file}")
        
    except Exception as e:
        print(f"✗ Export failed: {str(e)}")
        raise


if __name__ == "__main__":
    # Create example diagrams
    example_diagrams = create_example_diagrams()
    
    # Export diagrams
    export_diagrams(example_diagrams)
    
    print("\nExample system architecture diagrams have been created and exported!")
    print("Check the 'docs' directory for the generated files.")