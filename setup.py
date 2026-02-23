#!/usr/bin/env python
"""Setup configuration for Excel to CMT Converter."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="excel-to-cmt-converter",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Convert Excel spreadsheets to CMT-compatible XML and ZIP packages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/excel-to-cmt-zip-converter",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/excel-to-cmt-zip-converter/issues",
        "Documentation": "https://github.com/yourusername/excel-to-cmt-zip-converter/blob/main/README.md",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Data Formats",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "openpyxl>=3.6.0",
        "numpy>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.0",
            "flake8>=3.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "excel-to-cmt=src.converter:main",
        ],
    },
)
