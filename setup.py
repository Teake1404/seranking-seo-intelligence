#!/usr/bin/env python3
"""
Setup script for SEO Insights MCP Server
"""

from setuptools import setup, find_packages

with open("README_MCP.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements_mcp.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="seo-insights-mcp",
    version="1.0.0",
    author="SEO Insights Team",
    author_email="contact@seoinsights.com",
    description="Advanced SEO analysis MCP server with anomaly detection, opportunity analysis, and competitive intelligence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/seo-insights-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "seo-insights-mcp=seo_insights_mcp:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
