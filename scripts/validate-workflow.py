#!/usr/bin/env python3
"""
Workflow validation script for local testing.

This script validates the diagram generation workflow locally before
running it in GitHub Actions, helping catch issues early.
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse


class WorkflowValidator:
    """Validates the diagram generation workflow locally."""
    
    def __init__(self, project_root: Path):
        """Initialize the validator with project root path."""
        self.project_root = project_root
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.temp_dir: Optional[Path] = None
    
    def validate_environment(self) -> bool:
        """Validate the local environment setup."""
        print("🔍 Validating environment...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            self.errors.append(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        else:
            print(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check for uv
        try:
            result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ uv: {result.stdout.strip()}")
            else:
                self.errors.append("uv package manager not found or not working")
        except FileNotFoundError:
            self.errors.append("uv package manager not installed")
        
        # Check for Java (needed for PlantUML)
        try:
            result = subprocess.run(['java', '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                # Java version is printed to stderr
                version_line = result.stderr.split('\n')[0]
                print(f"✓ Java: {version_line}")
            else:
                self.warnings.append("Java not found - PlantUML rendering will fail")
        except FileNotFoundError:
            self.warnings.append("Java not installed - PlantUML rendering will fail")
        
        return len(self.errors) == 0
    
    def validate_project_structure(self) -> bool:
        """Validate the project structure."""
        print("🔍 Validating project structure...")
        
        required_files = [
            'pyproject.toml',
            'src/diagrams/__init__.py',
            'src/diagrams/generator.py',
            'src/diagrams/utils.py',
            'src/diagrams/example_system.py',
            '.github/workflows/render-diagrams.yml'
        ]
        
        required_dirs = [
            'src/diagrams',
            'tests',
            'templates',
            '.github/workflows'
        ]
        
        # Check required files
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"✓ {file_path}")
            else:
                self.errors.append(f"Missing required file: {file_path}")
        
        # Check required directories
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.is_dir():
                print(f"✓ {dir_path}/")
            else:
                self.errors.append(f"Missing required directory: {dir_path}")
        
        return len(self.errors) == 0
    
    def validate_dependencies(self) -> bool:
        """Validate that dependencies can be installed."""
        print("🔍 Validating dependencies...")
        
        try:
            # Try to sync dependencies
            result = subprocess.run(
                ['uv', 'sync', '--frozen'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print("✓ Dependencies sync successful")
                
                # Try to import key modules
                import_tests = [
                    ('pystructurizr', 'pystructurizr'),
                    ('src.diagrams.generator', 'DiagramGenerator'),
                    ('src.diagrams.utils', 'validate_diagram_elements')
                ]
                
                for module, item in import_tests:
                    try:
                        result = subprocess.run([
                            'uv', 'run', 'python', '-c',
                            f'from {module} import {item}; print("✓ {module}.{item}")'
                        ], cwd=self.project_root, capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            print(result.stdout.strip())
                        else:
                            self.errors.append(f"Failed to import {module}.{item}: {result.stderr}")
                    except Exception as e:
                        self.errors.append(f"Import test failed for {module}.{item}: {e}")
                
            else:
                self.errors.append(f"Dependency sync failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.errors.append("Dependency installation timed out")
        except Exception as e:
            self.errors.append(f"Dependency validation failed: {e}")
        
        return len(self.errors) == 0
    
    def validate_diagram_generation(self) -> bool:
        """Validate that diagram generation works."""
        print("🔍 Validating diagram generation...")
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            self.temp_dir = Path(temp_dir)
            
            try:
                # Run diagram generation
                result = subprocess.run([
                    'uv', 'run', 'python', 'src/diagrams/example_system.py'
                ], cwd=self.project_root, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print("✓ Diagram generation completed")
                    print(f"Output: {result.stdout}")
                    
                    # Check for generated files
                    docs_dir = self.project_root / 'docs'
                    if docs_dir.exists():
                        json_files = list(docs_dir.glob('*.json'))
                        puml_files = list(docs_dir.glob('*.puml'))
                        
                        if json_files:
                            print(f"✓ Generated {len(json_files)} JSON file(s)")
                            
                            # Validate JSON structure
                            for json_file in json_files:
                                try:
                                    with open(json_file) as f:
                                        data = json.load(f)
                                    
                                    required_sections = ['workspace', 'metadata']
                                    for section in required_sections:
                                        if section not in data:
                                            self.errors.append(f"Missing section '{section}' in {json_file}")
                                        else:
                                            print(f"✓ {json_file} has valid structure")
                                            
                                except json.JSONDecodeError as e:
                                    self.errors.append(f"Invalid JSON in {json_file}: {e}")
                        else:
                            self.warnings.append("No JSON files generated")
                        
                        if puml_files:
                            print(f"✓ Generated {len(puml_files)} PlantUML file(s)")
                            
                            # Validate PlantUML structure
                            for puml_file in puml_files:
                                try:
                                    with open(puml_file) as f:
                                        content = f.read()
                                    
                                    if '@startuml' not in content:
                                        self.errors.append(f"Missing @startuml in {puml_file}")
                                    elif '@enduml' not in content:
                                        self.errors.append(f"Missing @enduml in {puml_file}")
                                    else:
                                        print(f"✓ {puml_file} has valid structure")
                                        
                                except Exception as e:
                                    self.errors.append(f"Error reading {puml_file}: {e}")
                        else:
                            self.warnings.append("No PlantUML files generated")
                    else:
                        self.warnings.append("No docs directory created")
                        
                else:
                    self.errors.append(f"Diagram generation failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                self.errors.append("Diagram generation timed out")
            except Exception as e:
                self.errors.append(f"Diagram generation validation failed: {e}")
        
        return len(self.errors) == 0
    
    def validate_workflow_yaml(self) -> bool:
        """Validate the GitHub Actions workflow YAML."""
        print("🔍 Validating workflow YAML...")
        
        workflow_file = self.project_root / '.github/workflows/render-diagrams.yml'
        
        if not workflow_file.exists():
            self.errors.append("Workflow file not found")
            return False
        
        try:
            import yaml
            
            with open(workflow_file) as f:
                workflow_data = yaml.safe_load(f)
            
            # Check required sections
            required_sections = ['name', 'on', 'jobs']
            for section in required_sections:
                if section not in workflow_data:
                    self.errors.append(f"Missing section '{section}' in workflow")
                else:
                    print(f"✓ Workflow has '{section}' section")
            
            # Check jobs structure
            if 'jobs' in workflow_data:
                jobs = workflow_data['jobs']
                if 'render-diagrams' not in jobs:
                    self.errors.append("Missing 'render-diagrams' job")
                else:
                    print("✓ Workflow has 'render-diagrams' job")
                    
                    job = jobs['render-diagrams']
                    if 'steps' not in job:
                        self.errors.append("Missing 'steps' in render-diagrams job")
                    else:
                        steps = job['steps']
                        print(f"✓ Workflow has {len(steps)} steps")
                        
                        # Check for critical steps
                        step_names = [step.get('name', '') for step in steps]
                        critical_steps = [
                            'Checkout repository',
                            'Set up Python',
                            'Install uv',
                            'Generate diagram definitions'
                        ]
                        
                        for critical_step in critical_steps:
                            if any(critical_step in name for name in step_names):
                                print(f"✓ Found critical step: {critical_step}")
                            else:
                                self.warnings.append(f"Missing critical step: {critical_step}")
            
        except ImportError:
            self.warnings.append("PyYAML not available - skipping detailed YAML validation")
        except Exception as e:
            self.errors.append(f"Workflow YAML validation failed: {e}")
        
        return len(self.errors) == 0
    
    def run_tests(self) -> bool:
        """Run the test suite."""
        print("🔍 Running tests...")
        
        try:
            result = subprocess.run([
                'uv', 'run', 'python', '-m', 'pytest', 'tests/', '-v'
            ], cwd=self.project_root, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✓ All tests passed")
                print(result.stdout)
            else:
                self.errors.append(f"Tests failed: {result.stderr}")
                print(f"Test output: {result.stdout}")
                
        except subprocess.TimeoutExpired:
            self.errors.append("Tests timed out")
        except Exception as e:
            self.errors.append(f"Test execution failed: {e}")
        
        return len(self.errors) == 0
    
    def generate_report(self) -> Dict:
        """Generate a validation report."""
        return {
            'timestamp': subprocess.run(['date', '-u', '+%Y-%m-%dT%H:%M:%S.000Z'], 
                                      capture_output=True, text=True).stdout.strip(),
            'validation_passed': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings)
        }
    
    def run_full_validation(self, skip_tests: bool = False) -> bool:
        """Run complete validation suite."""
        print("🚀 Starting workflow validation...\n")
        
        validation_steps = [
            ('Environment', self.validate_environment),
            ('Project Structure', self.validate_project_structure),
            ('Dependencies', self.validate_dependencies),
            ('Diagram Generation', self.validate_diagram_generation),
            ('Workflow YAML', self.validate_workflow_yaml),
        ]
        
        if not skip_tests:
            validation_steps.append(('Tests', self.run_tests))
        
        all_passed = True
        
        for step_name, step_func in validation_steps:
            print(f"\n{'='*50}")
            print(f"Validating: {step_name}")
            print('='*50)
            
            try:
                step_passed = step_func()
                if not step_passed:
                    all_passed = False
                    print(f"❌ {step_name} validation failed")
                else:
                    print(f"✅ {step_name} validation passed")
            except Exception as e:
                self.errors.append(f"{step_name} validation error: {e}")
                all_passed = False
                print(f"💥 {step_name} validation crashed: {e}")
        
        # Generate final report
        print(f"\n{'='*50}")
        print("VALIDATION SUMMARY")
        print('='*50)
        
        if all_passed:
            print("🎉 All validations passed! Workflow should work correctly.")
        else:
            print("❌ Validation failed. Please fix the issues below:")
            
            if self.errors:
                print(f"\n🚨 ERRORS ({len(self.errors)}):")
                for i, error in enumerate(self.errors, 1):
                    print(f"  {i}. {error}")
            
            if self.warnings:
                print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
                for i, warning in enumerate(self.warnings, 1):
                    print(f"  {i}. {warning}")
        
        return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Validate diagram generation workflow')
    parser.add_argument('--skip-tests', action='store_true', 
                       help='Skip running the test suite')
    parser.add_argument('--project-root', type=Path, default=Path.cwd(),
                       help='Project root directory (default: current directory)')
    parser.add_argument('--report', type=Path,
                       help='Save validation report to JSON file')
    
    args = parser.parse_args()
    
    # Validate project root
    if not args.project_root.exists():
        print(f"❌ Project root does not exist: {args.project_root}")
        sys.exit(1)
    
    if not (args.project_root / 'pyproject.toml').exists():
        print(f"❌ Not a valid project root (no pyproject.toml): {args.project_root}")
        sys.exit(1)
    
    # Run validation
    validator = WorkflowValidator(args.project_root)
    success = validator.run_full_validation(skip_tests=args.skip_tests)
    
    # Save report if requested
    if args.report:
        report = validator.generate_report()
        with open(args.report, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Validation report saved to: {args.report}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()