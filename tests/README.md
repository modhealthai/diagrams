# Testing Documentation

This directory contains comprehensive tests for the pystructurizr-github-pages project.

## Test Structure

### Unit Tests
- `test_diagram_generator.py` - Tests for the DiagramGenerator class and related functionality
- `test_utils.py` - Tests for utility functions, configuration loading, and helper classes
- `test_site_generator.py` - Tests for the SiteGenerator class and static site generation
- `test_example_system.py` - Tests for the example e-commerce system diagrams

### Integration Tests
- `test_integration.py` - End-to-end integration tests covering the complete workflow

### Configuration
- `conftest.py` - Shared fixtures and pytest configuration
- `pytest.ini` - Pytest configuration file
- `README.md` - This documentation file

## Running Tests

### Using the Test Runner Script
The project includes a convenient test runner script:

```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --unit

# Run only integration tests
python run_tests.py --integration

# Run tests with coverage report
python run_tests.py --coverage

# Run tests from a specific file
python run_tests.py --file test_diagram_generator.py

# Run a specific test function
python run_tests.py --test test_create_workspace

# Skip slow tests
python run_tests.py --fast

# Verbose output
python run_tests.py --verbose
```

### Using pytest directly
You can also run tests directly with pytest:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run only unit tests
pytest tests/ -m unit

# Run only integration tests
pytest tests/ -m integration

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_diagram_generator.py

# Run specific test function
pytest tests/test_diagram_generator.py::TestDiagramGenerator::test_create_workspace
```

## Test Categories

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests for complete workflows
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.workflow` - Tests related to GitHub Actions workflows

## Test Coverage

The tests cover the following areas:

### DiagramGenerator (`test_diagram_generator.py`)
- Configuration and initialization
- Workspace creation and management
- View creation (system context, container, component)
- JSON and PlantUML export functionality
- Data validation and error handling
- Metadata management

### Utilities (`test_utils.py`)
- Configuration loading from YAML/JSON files
- Element factory methods for creating diagram elements
- Relationship management between elements
- Styling and theming functionality
- Diagram patterns and templates
- Validation functions

### Site Generator (`test_site_generator.py`)
- Site configuration and initialization
- Diagram metadata loading from files
- HTML template processing with Jinja2
- Static site generation (index, listing, individual pages)
- Navigation structure creation
- Asset copying and sitemap generation

### Example System (`test_example_system.py`)
- E-commerce system diagram creation
- System context, container, and component views
- Relationship creation between elements
- Export functionality with validation
- Metadata generation

### Integration Tests (`test_integration.py`)
- Complete diagram generation pipeline
- Site generation workflow
- GitHub Actions workflow validation
- End-to-end file operations
- Error handling and recovery

## Test Data and Fixtures

The test suite uses several shared fixtures defined in `conftest.py`:

- `sample_diagram_config` - Sample DiagramConfig for testing
- `sample_site_config` - Sample SiteConfig for testing
- `sample_diagram_metadata` - Sample diagram metadata objects
- `temp_workspace` - Temporary directory structure for testing
- `mock_pystructurizr_workspace` - Mock pystructurizr Workspace
- `mock_pystructurizr_elements` - Mock pystructurizr elements
- `sample_json_export` - Sample JSON export data
- `sample_plantuml_export` - Sample PlantUML export data
- `sample_html_templates` - Sample HTML templates

## Mocking Strategy

The tests use extensive mocking to isolate components and avoid dependencies on external libraries:

- **pystructurizr library** - Mocked to avoid requiring the actual library
- **File system operations** - Mocked for predictable test behavior
- **Jinja2 templates** - Mocked for template rendering tests
- **External processes** - Mocked for GitHub Actions workflow tests

## Best Practices

The test suite follows these best practices:

1. **Isolation** - Each test is independent and doesn't rely on others
2. **Mocking** - External dependencies are mocked to ensure reliability
3. **Coverage** - Tests cover both success and failure scenarios
4. **Documentation** - Each test has clear docstrings explaining its purpose
5. **Organization** - Tests are grouped by functionality and marked appropriately
6. **Fixtures** - Common test data is shared through fixtures
7. **Assertions** - Tests use specific assertions with clear error messages

## Continuous Integration

The tests are designed to run in CI environments:

- No external dependencies required (everything is mocked)
- Fast execution (slow tests are marked and can be skipped)
- Clear output and error reporting
- Coverage reporting integration
- Multiple Python version compatibility

## Adding New Tests

When adding new tests:

1. Place them in the appropriate test file based on functionality
2. Use descriptive test names that explain what is being tested
3. Add appropriate pytest markers (`@pytest.mark.unit`, etc.)
4. Use existing fixtures where possible
5. Mock external dependencies
6. Test both success and failure scenarios
7. Add docstrings explaining the test purpose

## Troubleshooting

Common issues and solutions:

### Import Errors
- Ensure the `src/` directory is in the Python path
- Check that all required dependencies are installed

### Mock Issues
- Verify mock patch paths are correct
- Ensure mocked objects have the expected attributes and methods

### File System Tests
- Use temporary directories for file operations
- Clean up test files after tests complete

### Slow Tests
- Mark slow tests with `@pytest.mark.slow`
- Use the `--fast` flag to skip them during development