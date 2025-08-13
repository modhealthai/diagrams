# PyStructurizr GitHub Pages

A Python project that uses pystructurizr for creating architectural diagrams and includes automated GitHub Actions workflow to render these diagrams and publish them to GitHub Pages. The project uses uv for modern Python package management and provides a streamlined workflow for maintaining and sharing architectural documentation.

## Features

- **Code-based Architecture Diagrams**: Create system context, container, and component diagrams using Python code with pystructurizr
- **Automated Rendering**: GitHub Actions workflow automatically renders diagrams to PNG/SVG formats using PlantUML
- **Static Site Generation**: Generates a beautiful, responsive website to showcase your architectural documentation
- **Modern Python Tooling**: Uses uv for fast, reliable dependency management and virtual environments
- **Multiple Export Formats**: Export diagrams as JSON metadata and PlantUML source code
- **Comprehensive Testing**: Full test suite with unit and integration tests

## Quick Start

### Prerequisites

- Python 3.9 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Git and GitHub account

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/pystructurizr-github-pages.git
   cd pystructurizr-github-pages
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Verify installation**:
   ```bash
   uv run python src/diagrams/example_system.py
   ```

### Creating Your First Diagram

1. **Create a new diagram file** in `src/diagrams/`:
   ```python
   # src/diagrams/my_system.py
   from diagrams.generator import DiagramGenerator, DiagramConfig
   from diagrams.utils import ElementFactory, ViewStyler
   
   def create_my_system():
       config = DiagramConfig(
           name="My System Architecture",
           description="Architecture for my awesome system",
           version="1.0.0"
       )
       
       generator = DiagramGenerator(config)
       workspace = generator.create_workspace()
       
       # Create elements
       user = ElementFactory.create_person("User", "System user")
       system = ElementFactory.create_software_system("My System", "Main application")
       
       # Create relationships
       user.uses(system, "Uses the application")
       
       # Create system context view
       view = generator.add_system_context_view(
           system,
           "My System - Context",
           "Shows the system and its users"
       )
       
       view.include(user)
       view.include(system)
       ViewStyler.apply_custom_theme(view, "modern")
       
       return generator
   
   if __name__ == "__main__":
       diagrams = create_my_system()
       # Export will be handled by the workflow
   ```

2. **Commit and push** to trigger the GitHub Actions workflow:
   ```bash
   git add .
   git commit -m "Add my system diagram"
   git push origin main
   ```

3. **View your diagrams** at `https://yourusername.github.io/pystructurizr-github-pages`

## Project Structure

```
pystructurizr-github-pages/
├── .github/
│   └── workflows/
│       └── render-diagrams.yml    # GitHub Actions workflow
├── src/
│   └── diagrams/
│       ├── __init__.py
│       ├── example_system.py      # Example e-commerce system diagrams
│       ├── generator.py           # Core diagram generation classes
│       └── utils.py               # Utility functions and helpers
├── templates/                     # Jinja2 templates for static site
│   ├── base.html                  # Base template with navigation
│   ├── index.html                 # Homepage template
│   ├── diagrams.html              # Diagrams listing template
│   └── diagram.html               # Individual diagram template
├── docs/                          # Generated output (GitHub Pages)
│   ├── index.html                 # Generated homepage
│   ├── diagrams/                  # Generated diagram pages
│   ├── images/                    # Rendered PNG/SVG images
│   └── *.json, *.puml            # Exported diagram data
├── tests/                         # Test suite
├── pyproject.toml                 # Project configuration and dependencies
├── generate_site.py               # Site generation script
└── README.md                      # This file
```

## Creating Different Types of Diagrams

### System Context Diagrams

Show your system and its interactions with users and external systems:

```python
def create_system_context():
    # Create people
    customer = ElementFactory.create_person("Customer", "Buys products")
    admin = ElementFactory.create_person("Admin", "Manages system")
    
    # Create systems
    ecommerce = ElementFactory.create_software_system("E-commerce", "Online store")
    payment = ElementFactory.create_software_system("Payment Gateway", "Processes payments")
    
    # Create relationships
    customer.uses(ecommerce, "Browses and buys products")
    admin.uses(ecommerce, "Manages products and orders")
    ecommerce.uses(payment, "Processes payments")
    
    # Create view
    view = generator.add_system_context_view(ecommerce, "System Context", "High-level view")
    view.include(customer, admin, ecommerce, payment)
```

### Container Diagrams

Show the internal structure of your system:

```python
def create_container_view():
    # Create containers within your system
    web_app = ecommerce.Container("Web App", "User interface", "React")
    api = ecommerce.Container("API", "Business logic", "Python/FastAPI")
    database = ecommerce.Container("Database", "Data storage", "PostgreSQL")
    
    # Create relationships
    web_app.uses(api, "Makes API calls", "HTTPS")
    api.uses(database, "Reads/writes data", "SQL")
    
    # Create view
    view = generator.add_container_view(ecommerce, "Container View", "Internal structure")
```

### Component Diagrams

Show the internal structure of a container:

```python
def create_component_view():
    # Create components within a container
    controller = api.Component("Order Controller", "Handles requests", "FastAPI")
    service = api.Component("Order Service", "Business logic", "Python")
    repository = api.Component("Order Repository", "Data access", "SQLAlchemy")
    
    # Create relationships
    controller.uses(service, "Delegates to")
    service.uses(repository, "Persists data via")
    
    # Create view
    view = generator.add_component_view(api, "Component View", "API internal structure")
```

## GitHub Actions Workflow

The project includes a comprehensive GitHub Actions workflow that:

1. **Sets up the environment** with Python and uv
2. **Installs dependencies** and verifies the installation
3. **Generates diagrams** by running your Python scripts
4. **Renders diagrams** to PNG/SVG using PlantUML
5. **Generates static site** with navigation and metadata
6. **Deploys to GitHub Pages** automatically

### Workflow Configuration

The workflow is triggered by:
- Pushes to the `main` branch
- Pull requests (for validation)
- Manual workflow dispatch

### Customizing the Workflow

You can customize the workflow by editing `.github/workflows/render-diagrams.yml`:

```yaml
# Add custom build steps
- name: Custom processing
  run: |
    # Your custom commands here
    uv run python custom_script.py

# Modify PlantUML rendering options
- name: Render diagrams with custom options
  run: |
    java -jar plantuml.jar -tpng -config custom.puml docs/*.puml
```

## Advanced Usage

### Custom Styling and Themes

Apply custom themes to your diagrams:

```python
from diagrams.utils import ViewStyler, StyleConfig

# Create custom style
custom_style = StyleConfig(
    colors={
        "person": "#2E4057",
        "software_system": "#048A81",
        "container": "#54C6EB"
    }
)

ViewStyler.apply_default_styles(view, custom_style)

# Or use predefined themes
ViewStyler.apply_custom_theme(view, "corporate")  # corporate, modern, minimal
```

### Configuration Files

Use YAML configuration files for complex setups:

```yaml
# diagram_config.yml
name: "My Architecture"
description: "System architecture documentation"
version: "2.0.0"
author: "Architecture Team"
output_formats:
  - json
  - plantuml
  - png
  - svg

styling:
  theme: "corporate"
  colors:
    person: "#2E4057"
    system: "#048A81"
```

Load configuration in your diagrams:

```python
from diagrams.utils import load_diagram_config

config_data = load_diagram_config("diagram_config.yml")
config = DiagramConfig(**config_data)
```

### Batch Processing

Generate multiple diagrams in one script:

```python
def generate_all_diagrams():
    systems = ["user_management", "order_processing", "inventory"]
    
    for system_name in systems:
        generator = create_system_diagrams(system_name)
        export_diagrams(generator, f"docs/{system_name}")
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test categories
uv run pytest tests/test_diagram_generator.py  # Unit tests
uv run pytest tests/test_integration.py       # Integration tests
```

### Writing Tests for Your Diagrams

```python
def test_my_system_diagram():
    generator = create_my_system()
    
    # Test that workspace was created
    assert generator.workspace is not None
    
    # Test that metadata is correct
    metadata = generator.get_metadata()
    assert len(metadata) > 0
    assert metadata[0].title == "My System - Context"
    
    # Test export functionality
    json_output = generator.export_to_json()
    assert "workspace" in json_output
```

## Troubleshooting

### Common Issues

**1. Import errors when running diagrams**
```bash
# Make sure you're in the project root and using uv
uv run python src/diagrams/example_system.py
```

**2. GitHub Actions workflow fails**
- Check that your Python syntax is correct
- Ensure all required dependencies are in pyproject.toml
- Verify that your diagram scripts can run locally

**3. PlantUML rendering issues**
- Check that your PlantUML syntax is valid
- Ensure Java is available in the GitHub Actions environment
- Verify PlantUML jar file download is successful

**4. GitHub Pages not updating**
- Check that GitHub Pages is enabled in repository settings
- Verify that the workflow has proper permissions
- Ensure the `docs/` directory contains generated files

### Debugging Tips

**Enable verbose logging in your diagrams**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your diagram code here
```

**Test diagram generation locally**:
```bash
# Generate diagrams and check output
uv run python src/diagrams/example_system.py
ls -la docs/

# Test site generation
uv run python generate_site.py
```

**Validate PlantUML output**:
```bash
# Check PlantUML syntax
java -jar plantuml.jar -checkonly docs/*.puml
```

### Getting Help

1. **Check the example diagrams** in `src/diagrams/example_system.py`
2. **Review the test files** in `tests/` for usage patterns
3. **Examine the generated output** in `docs/` after running locally
4. **Check GitHub Actions logs** for detailed error messages

## Contributing

We welcome contributions! Here's how to get started:

### Development Setup

1. **Fork and clone the repository**
2. **Install development dependencies**:
   ```bash
   uv sync --dev
   ```
3. **Install pre-commit hooks**:
   ```bash
   uv run pre-commit install
   ```

### Code Quality

We maintain high code quality standards:

```bash
# Format code
uv run black src/ tests/
uv run isort src/ tests/

# Lint code
uv run flake8 src/ tests/

# Type checking
uv run mypy src/

# Run all quality checks
uv run pytest --cov=src --cov-report=term-missing
```

### Contribution Guidelines

1. **Follow the existing code style** (Black, isort, flake8)
2. **Add tests** for new functionality
3. **Update documentation** for new features
4. **Write clear commit messages**
5. **Create focused pull requests**

### Adding New Features

When adding new features:

1. **Create an issue** describing the feature
2. **Write tests first** (TDD approach)
3. **Implement the feature** with proper documentation
4. **Update examples** if applicable
5. **Add to the changelog**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [pystructurizr](https://github.com/Midnighter/pystructurizr) for the Python Structurizr implementation
- [PlantUML](https://plantuml.com/) for diagram rendering
- [GitHub Actions](https://github.com/features/actions) for CI/CD automation
- [GitHub Pages](https://pages.github.com/) for static site hosting

## Changelog

### v0.1.0 (Current)
- Initial release with basic diagram generation
- GitHub Actions workflow for automated rendering
- Static site generation with responsive templates
- Comprehensive test suite
- Example e-commerce system diagrams