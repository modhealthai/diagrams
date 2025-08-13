# PyStructurizr GitHub Pages

A Python project for creating architectural diagrams with pystructurizr and publishing them to GitHub Pages.

## Features

- Create architectural diagrams using Python code
- Automated GitHub Actions workflow for rendering diagrams
- Publish diagrams to GitHub Pages
- Modern Python tooling with uv package management

## Getting Started

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Create your diagrams in the `src/diagrams/` directory

3. Push to GitHub to trigger automatic rendering and publishing

## Project Structure

- `src/diagrams/` - Diagram definitions and utilities
- `.github/workflows/` - GitHub Actions workflow
- `templates/` - HTML templates for GitHub Pages
- `docs/` - Generated documentation and diagrams