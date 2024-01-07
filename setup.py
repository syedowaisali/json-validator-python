import pathlib

from setuptools import setup, find_packages

# The directory containing this file
here = pathlib.Path(__file__).parent

# The text of the README file
README = (here/"README.md").read_text()
github_url = "https://github.com/syedowaisali/json-validator-python"

setup(
    name="jsvl",
    version="1.0.8",
    url=github_url,
    project_urls={
        'Issues': f'{github_url}/issues',
        'Source Code': github_url,
    },
    author="Syed Owais Ali",
    author_email="dp.owaisali@gmail.com",
    descp="JSON Validator is a feature-rich Python library designed to elevate the validation of JSON documents by offering an extensive schema-based validation system.",
    long_description=README,
    long_description_content_type="text/markdown",
    keywords="python json schema validation",
    packages=find_packages(),
    install_requires=[
        'ordered_set',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    license="GPL",
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "jsvl = jsvl.cli:run_validation",
        ],
    },
)