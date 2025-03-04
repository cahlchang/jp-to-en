#!/usr/bin/env python3
from setuptools import setup, find_packages

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jp-to-en",
    version="0.1.0",
    author="cahlchang",
    author_email="cahlchang@gmail.com",
    description="A CLI tool to convert Japanese comments in code to English",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cahlchang/jp-to-en",
    packages=["jp_to_en", "jp_to_en.detector", "jp_to_en.parser",
              "jp_to_en.translator", "jp_to_en.formatter"],
    include_package_data=True,
    package_data={
        "jp_to_en": ["config/*.json"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "openai>=1.0.0",
        "langdetect>=1.0.9",
        "rich>=13.0.0",
        "regex>=2023.0.0",
    ],
    entry_points={
        "console_scripts": [
            "jp-to-en=jp_to_en.main:main",
        ],
    },
)
