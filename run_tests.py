#!/usr/bin/env python3
"""
Test runner script for the pystructurizr-github-pages project.

This script provides a convenient way to run different types of tests
with various options and configurations.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return the result."""
    if description:
        print(f"\n{description}")
        print("=" * len(description))
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False, text=True)
    return result.returncode == 0


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run tests for pystructurizr-github-pages")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--file", help="Run tests from specific file")
    parser.add_argument("--test", help="Run specific test function")
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test directory
    if args.file:
        cmd.append(f"tests/{args.file}")
    else:
        cmd.append("tests/")
    
    # Add specific test if provided
    if args.test:
        cmd[-1] += f"::{args.test}"
    
    # Add markers for test selection
    if args.unit:
        cmd.extend(["-m", "unit"])
    elif args.integration:
        cmd.extend(["-m", "integration"])
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend([
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=80"
        ])
    
    # Add verbose output
    if args.verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Skip slow tests if requested
    if args.fast:
        cmd.extend(["-m", "not slow"])
    
    # Add other useful options
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--color=yes"
    ])
    
    # Run the tests
    success = run_command(cmd, "Running Tests")
    
    if not success:
        print("\n❌ Tests failed!")
        return 1
    
    print("\n✅ All tests passed!")
    
    # Run additional checks if all tests pass
    if not args.file and not args.test:
        print("\n" + "="*50)
        print("Running additional code quality checks...")
        
        # Run type checking
        type_check_success = run_command(
            ["python", "-m", "mypy", "src/", "--ignore-missing-imports"],
            "Type Checking with MyPy"
        )
        
        # Run code formatting check
        format_check_success = run_command(
            ["python", "-m", "black", "--check", "src/", "tests/"],
            "Code Formatting Check"
        )
        
        # Run import sorting check
        import_check_success = run_command(
            ["python", "-m", "isort", "--check-only", "src/", "tests/"],
            "Import Sorting Check"
        )
        
        if not all([type_check_success, format_check_success, import_check_success]):
            print("\n⚠️  Some code quality checks failed!")
            return 1
        
        print("\n✅ All checks passed!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())