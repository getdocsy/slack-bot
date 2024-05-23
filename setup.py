#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="docsy",
    version="1.0",
    packages=find_packages(),
    scripts=[
        "docsy_slack.py",
        "documentation_assistant.py",
        "github_manager.py",
    ],
)
