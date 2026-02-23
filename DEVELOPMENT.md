# Development Guide

## Setup Development Environment

### 1. Clone and Create Virtual Environment

```bash
git clone <repository-url>
cd excel-to-cmt-zip-converter
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Development Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-cov black flake8
```

### 3. Project Structure

- `src/` - Main application code
  - `__init__.py` - Package initialization
  - `config.py` - Configuration settings
  - `converter.py` - Main conversion logic
  - `excel_loader.py` - Excel file handling
  - `schema_loader.py` - Schema parsing
  - `utils.py` - Utility functions
  - `xml_generator.py` - XML generation

- `tests/` - Test files
  - `test_converter.py` - Converter tests

- `inputs/` - Input data (not committed to git)
- `outputs/` - Generated output (not committed to git)

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/

# Run specific test file
python -m pytest tests/test_converter.py -v
```

## Code Style

### Format Code

```bash
black src/ tests/
```

### Check Code Quality

```bash
flake8 src/ tests/
```

## Making Changes

1. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes:**
   - Write clean, documented code
   - Follow PEP 8 style guide
   - Add docstrings to functions/classes
   - Add type hints where possible

3. **Test your changes:**
   ```bash
   python -m pytest tests/ -v
   ```

4. **Format and lint:**
   ```bash
   black src/
   flake8 src/
   ```

5. **Commit and push:**
   ```bash
   git commit -m "feat: description of changes"
   git push origin feature/your-feature-name
   ```

## Adding New Features

### Example: Adding a new module

1. Create `src/new_module.py` with proper docstrings
2. Add imports to `src/__init__.py`
3. Create corresponding tests in `tests/test_new_module.py`
4. Update documentation in README.md

### Code Style Guidelines

```python
"""Module docstring at top of file."""

from typing import Dict, List, Optional
from pathlib import Path


class MyClass:
    """Class docstring."""

    def __init__(self, param: str) -> None:
        """Initialize docstring."""
        self.param = param

    def my_method(self, arg: int) -> str:
        """Method docstring."""
        return str(arg)


def my_function(value: int) -> int:
    """Function docstring."""
    return value * 2
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test with Sample Data

1. Create sample Excel file in `inputs/test_project/`
2. Create corresponding schema XML
3. Run converter with `python -c "from src import main; main('test_project')"`

## Documentation

- Update README.md when adding user-facing features
- Add docstrings to all public functions/classes
- Include type hints for better IDE support
- Document configuration changes in README

## Release Process

1. Update version in `src/__init__.py`
2. Update CHANGELOG (if maintained)
3. Create git tag: `git tag v1.0.0`
4. Push: `git push origin main --tags`

## Common Issues

### Import Errors
- Ensure virtual environment is activated
- Reinstall: `pip install -e .`

### Test Failures
- Check that inputs/outputs directories exist
- Verify test data files are in place
- Review recent changes for breaking updates

### File Path Issues
- Use `Path` from `pathlib` for cross-platform compatibility
- Avoid hardcoded paths - use `config.py` values
