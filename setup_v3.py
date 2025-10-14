#!/usr/bin/env python3
"""Setup script for cbhands v3.0.0."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements_v3.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cbhands",
    version="3.0.0",
    author="Battle Hands Team",
    description="Extensible service manager for Battle Hands with plugin system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "rich": ["rich>=13.0.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cbhands=cbhands.v3.main:main",
            "cbhands-v3=cbhands.v3.main:main",
        ],
        "cbhands.plugins": [
            # Plugins will be registered here
        ],
    },
    include_package_data=True,
    package_data={
        "cbhands": ["config/*.yaml", "templates/*.yaml"],
    },
    project_urls={
        "Homepage": "https://github.com/j0k/cbhands",
        "Bug Reports": "https://github.com/j0k/cbhands/issues",
        "Source": "https://github.com/j0k/cbhands",
        "Documentation": "https://github.com/j0k/cbhands/blob/main/README.md",
    },
)
