"""
FlowForge setup.py
"""
from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flowforge",
    version="0.1.0",
    description="Event-driven workflow orchestration framework with flexible connection, state management, and workflow orchestration capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="FlowForge Team",
    author_email="",
    url="https://github.com/flowforge/flowforge",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "docs"]),
    python_requires=">=3.7",
    install_requires=[
        # Core dependencies - to be specified when available
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinx-autodoc-typehints>=1.19.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license="Apache-2.0",
    keywords="workflow routine orchestration state-management",
    include_package_data=True,
    zip_safe=False,
)

