# click-wrapper

[![PyPI](https://img.shields.io/pypi/v/click-wrapper.svg)](https://pypi.org/project/click-wrapper/)
[![Changelog](https://img.shields.io/github/v/release/mse11/click-wrapper?include_prereleases&label=changelog)](https://github.com/mse11/click-wrapper/releases)
[![Tests](https://github.com/mse11/click-wrapper/actions/workflows/test.yml/badge.svg)](https://github.com/mse11/click-wrapper/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/mse11/click-wrapper/blob/master/LICENSE)

Wrapper for clAutomatic Python wrapper generator for Click CLI applications. Generate type-safe dataclasses and wrapper methods from Click command introspection

## Installation

Install this tool using `pip`:
```bash
pip install click-wrapper
```
## Usage

For help, run:
```bash
click-wrapper --help
```
You can also use:
```bash
python -m click_wrapper --help
```
## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:
```bash
cd click-wrapper
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
