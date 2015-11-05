#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="Roach",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "CherryPy==3.8.0"
    ],
    entry_points={
        "console_scripts": [
            "roach = roach.entry_point:main",
            "roach_webapp = roach_webapp.app:main"
        ]
    },
    package_data={
        "": ["*.js", "*.css", "*.html"]
    }
)
