"""
Setup file for risk_package
"""
from setuptools import setup, find_packages

setup(
    name="risk_package",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "psycopg2-binary>=2.9.0"
    ],
    python_requires=">=3.8",
    description="Monte Carlo risk calculation package for distributed computing",
    author="Your Name",
)