# DP Wizard - Copilot Coding Agent Instructions

## Repository Overview

**DP Wizard** is a Python web application that makes it easier to get started with differential privacy. Built with Python Shiny, it provides an interactive interface for users to upload CSV data, configure privacy parameters, and generate differential privacy analyses including Jupyter notebooks, Python scripts, and reports.

### High-Level Details
- **Project Type**: Python web application using Shiny framework
- **Primary Languages**: Python 3.10+ (currently tested on 3.10 and 3.13)
- **Framework**: Python Shiny for web UI
- **Size**: ~65 Python files in repository
- **Main Dependencies**: OpenDP library, Python Shiny, matplotlib, playwright (for testing)
- **Target Runtime**: Python 3.10+, browser-based frontend
- **Distribution**: PyPI package (`dp_wizard`), installable with pip

## Build Instructions & Development Workflow

### Environment Setup (CRITICAL - Always Required)
1. **Python Version**: Use Python 3.10+ (Python 3.10 recommended for fewest surprises)
2. **Virtual Environment**: Always create and activate a virtual environment:
   ```bash
   python3.10 -m venv .venv
   # On macOS/Linux:
   source .venv/bin/activate
   # On Windows (cmd.exe):
   .venv\Scripts\activate
   ```

### Development Dependencies Installation (REQUIRED ORDER)
**ALWAYS run these commands in this exact order:**
```bash
# 1. Install flit first
pip install flit

# 2. Install the package in editable mode
flit install

# 3. Install dev dependencies (this step may take several minutes)
pip install -r requirements-dev.txt

# 4. Install pre-commit hooks
pre-commit install

# 5. Install playwright browsers (required for testing)
playwright install
```

**Note**: If `flit install` fails due to network timeouts, retry with longer timeout or install dependencies manually from requirements-dev.txt first.

### Building and Testing (Critical Commands)

#### Run All Tests and Checks
```bash
# Primary CI command - runs all tests, coverage, and validation
scripts/ci.sh
```
**Timing**: This command typically takes 3-5 minutes to complete.

#### Alternative Testing Modes
```bash
# Run tests in parallel (faster for development)
pytest -vv --failed-first --durations=5 --numprocesses=auto --cov=.

# Run tests in single process (for CI/debugging)
CI=true scripts/ci.sh
```

#### Code Quality Checks
```bash
# Run linting and formatting
flake8
black --check .
isort --check-only .

# Fix formatting issues
black .
isort .
```

#### Manual App Testing
```bash
# Run with sample data (recommended for quick testing)
dp-wizard --sample

# Run with cloud mode (column names only)
dp-wizard --cloud

# Run locally (full CSV upload)
dp-wizard
```
**Note**: First startup may take a minute; successive runs are faster.

### Dependency Management (Important Process)
When adding new dependencies:
1. Add to `requirements.in` (runtime deps) or `requirements-dev.in` (dev deps)
2. Run `scripts/requirements.py` to update lock files and pyproject.toml
3. This script handles pip-compile and updates the TOML configuration automatically

### Testing with Playwright
- **End-to-end tests**: Use `pytest -k test_app` for browser-based tests
- **Test debugging**: Set `PWDEBUG=1 pytest -k test_app` to step through tests
- **Test generation**: Use `playwright codegen http://127.0.0.1:8000/` to generate test code
- **Coverage Note**: App code is skipped by test coverage during e2e tests due to separate ASGI process

## Project Layout & Architecture

### Root Directory Structure
```
dp-wizard/
├── .github/                 # GitHub configurations
│   └── workflows/test.yml   # CI/CD pipeline
├── dp_wizard/              # Main application code
├── tests/                  # Test files (pytest + playwright)
├── scripts/                # Build and deployment scripts
├── pyproject.toml          # Package configuration
├── requirements*.txt       # Dependency specifications
├── .flake8                 # Linting configuration
├── .pytest.ini            # Pytest configuration
├── .pre-commit-config.yaml # Pre-commit hook configuration
└── .coveragerc            # Coverage configuration
```

### Application Architecture
- **Entry Points**: 
  - `dp_wizard/app_local.py` - Main local app with CSV upload
  - `dp_wizard/app_cloud.py` - Cloud app (column names only)
  - `dp_wizard/app_sample.py` - Sample data demo
  - `dp_wizard/app_qa.py` - QA/testing mode
- **Main Module**: `dp_wizard/__init__.py` contains main() function
- **Utils**: `dp_wizard/utils/` - Code generation, CSV helpers, shared utilities
- **Shiny Components**: `dp_wizard/shiny/` - UI modules and components

### Configuration Files
- **Linting**: `.flake8` (excludes templates in `no-tests/` directories)
- **Testing**: `.pytest.ini` (excludes templates, enables tracing)
- **Coverage**: `.coveragerc` (100% coverage required, omits fixtures)
- **Pre-commit**: `.pre-commit-config.yaml` (yaml check, formatting, trailing whitespace)
- **Type Checking**: `pyproject.toml` includes pyright configuration

### Testing Structure
- **Unit Tests**: `tests/utils/` - Test utility functions
- **E2E Tests**: `tests/test_app.py` - Full application testing with playwright
- **Fixtures**: `tests/fixtures/` - Test data and shared test utilities
- **Test Configuration**: Strict xfail, doctests enabled, warnings as errors

## Validation Pipeline & CI/CD

### GitHub Workflow (`.github/workflows/test.yml`)
**Matrix Testing**:
- Python versions: 3.10, 3.13
- Requirements: both pinned (requirements-dev.txt) and unpinned (requirements-dev.in)

**CI Steps** (executed in this order):
1. Install flit
2. Install package with flit
3. Install dev dependencies
4. Install chromium browser only (instead of all browsers)
5. Run `scripts/ci.sh`
6. Upload playwright traces on failure

### Pre-commit Hooks
Automatically run on commit:
- YAML syntax checking
- End-of-file fixers
- Trailing whitespace removal
- Black code formatting
- Isort import sorting

### Release Process
1. Create feature branch with version number
2. Run `scripts/changelog.py` to update CHANGELOG.md
3. Update `dp_wizard/VERSION` file
4. Merge to main
5. Publish with `flit publish --pypirc .pypirc`

### Cloud Deployment
- Cloud deployment updates automatically on pushes to `cloud-deployment` branch
- Use `scripts/deploy.sh` to deploy from main branch (requires tests to pass)

## Key Development Notes

### Branch Naming Convention
Use format: `NNNN-short-description` where NNNN is the GitHub issue number

### Python Shiny Specific Considerations
- **No component testing available** - Use unit tests for logic, e2e tests for UI
- **Module IDs must be alphanumeric + underscore only** - Cannot use arbitrary strings
- **Silent failures** possible with ID mismatches between UI and server functions
- **Reactive values vs plain values** - Be consistent in naming/typing
- **First startup warning** - App shows warning on first run, creates `tmp/not-first-run.txt`

### Common Gotchas & Workarounds
- **Network timeouts during install**: Retry flit install or install requirements-dev.txt first
- **Playwright test debugging**: Use `PWDEBUG=1` and `page.pause()` instead of `breakpoint()`
- **Template files excluded**: Files in `no-tests/` directories are excluded from linting/coverage
- **Coverage requirements**: 100% coverage required except explicitly ignored blocks
- **Memory issues**: Large dependency tree may cause memory issues in constrained environments

### File Patterns to Recognize
- **Templates**: `**/no-tests/*.py` - Code generation templates (excluded from tests/linting)
- **Analysis modules**: `dp_wizard/utils/code_generators/analyses/*/` - Specific DP analysis types
- **Shiny modules**: `dp_wizard/shiny/` - UI components and modules

## Trust These Instructions

**IMPORTANT**: Trust these instructions and only search for additional information if the instructions are incomplete or you discover errors. The build process and dependency management have been thoroughly tested. Follow the exact command sequences provided to avoid common pitfalls.

When in doubt about testing or building, always run `scripts/ci.sh` as it replicates the exact CI environment and will catch issues before they reach the GitHub pipeline.