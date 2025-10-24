# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Type

This is a Python project based on the .gitignore configuration.

## Development Setup

### Python Environment
- Use virtual environments (.venv, venv, or env) for dependency isolation
- Environment files (.env, .envrc) are gitignored and should contain sensitive configuration

### Common Commands

Since no package manager configuration exists yet, when setting up the project:
- For pip-based projects: `pip install -r requirements.txt` (if requirements.txt exists)
- For poetry projects: `poetry install` (if pyproject.toml exists)
- For pipenv projects: `pipenv install` (if Pipfile exists)

### Testing
Check for test files in common locations:
- `tests/` directory for pytest or unittest tests
- `test_*.py` files for test modules
- Run tests with appropriate framework once determined

### Code Quality
When Python tooling is set up, use:
- `ruff` for linting (per .gitignore, ruff cache is present)
- `mypy` for type checking (mypy cache is gitignored)

## Important Notes

- The project uses ruff for Python linting (evident from .ruff_cache/ in .gitignore)
- Type checking with mypy is likely used (mypy cache directories are gitignored)
- Marimo notebook support may be present (marimo directories are gitignored)