from setuptools import setup, find_packages

setup(
    name="omniplan_exporter",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "isodate",
        "pytest",
        "pytest-watch",
    ],
    entry_points={
        "console_scripts": [
            "omniplan-sync=omniplan_exporter.sync:main",
        ],
    },
)
