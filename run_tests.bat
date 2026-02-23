@echo off
REM Run tests for Excel to XML Converter

echo.
echo ========================================
echo Excel to XML Converter - Test Runner
echo ========================================
echo.

if "%1"=="" (
    echo Running all tests...
    python -m pytest tests/ -v
) else if "%1"=="unit" (
    echo Running unit tests only...
    python -m pytest tests/test_converter.py::TestConverterSetup -v
    python -m pytest tests/test_converter.py::TestUtilityFunctions -v
) else if "%1"=="integration" (
    echo Running integration tests only...
    python -m pytest tests/test_converter.py::TestConversionIntegration -v
) else if "%1"=="coverage" (
    echo Running tests with coverage...
    python -m pytest tests/ --cov=src --cov-report=html
    echo.
    echo Coverage report generated in htmlcov/index.html
) else if "%1"=="quick" (
    echo Running quick validation...
    python -m pytest tests/test_converter.py::TestConverterSetup -v
    python -m pytest tests/test_converter.py::TestUtilityFunctions -v
) else (
    echo.
    echo Usage: run_tests.bat [option]
    echo.
    echo Options:
    echo   (none)        Run all tests
    echo   unit          Run only unit tests
    echo   integration   Run only integration tests  
    echo   coverage      Run tests with coverage report
    echo   quick         Run quick tests ^(setup + utils^)
    echo.
)

echo.
echo ========================================
echo Test run complete
echo ========================================
