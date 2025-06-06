#!/usr/bin/env python3
"""
Setup script for Universal LLMs.txt Generator
"""
from setuptools import setup, find_packages
import os
import sys

# Ensure we're using Python 3.8+
if sys.version_info < (3, 8):
    sys.exit('Python 3.8 or higher is required')

# Read README for long description
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
def read_requirements(filename):
    with open(os.path.join(this_directory, filename), encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

requirements = read_requirements('requirements.txt')

setup(
    name="universal-llms-txt-generator",
    version="1.0.0",
    author="AsifMinar",
    author_email="asifminar.dev@gmail.com",
    description="Universal tool to generate and maintain llms.txt files for any website stack",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AsifMinar/Universal-LLMS.txt-Generator",
    project_urls={
        "Bug Reports": "https://github.com/AsifMinar/Universal-LLMS.txt-Generator/issues",
        "Source": "https://github.com/AsifMinar/Universal-LLMS.txt-Generator",
        "Documentation": "https://github.com/AsifMinar/Universal-LLMS.txt-Generator/wiki",
        "Funding": "https://github.com/sponsors/AsifMinar",
    },
    packages=find_packages(where="src") if os.path.exists("src") else ["."],
    package_dir={"": "src"} if os.path.exists("src") else {},
    py_modules=["llms_txt_generator"] if not os.path.exists("src") else [],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Utilities",
    ],
    keywords="llms llmstxt ai ml sitemap robots.txt wordpress django flask static-site",
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": read_requirements('requirements-dev.txt'),
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "responses>=0.23.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "llms-txt-gen=llms_txt_generator:main",
            "llms-txt-generator=llms_txt_generator:main",
            "universal-llms-txt=llms_txt_generator:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.md", "*.txt"],
    },
    zip_safe=False,
    platforms=["any"],
    license="MIT",
    test_suite="tests",
)