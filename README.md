# click-wrapper

[![PyPI](https://img.shields.io/pypi/v/click-wrapper.svg)](https://pypi.org/project/click-wrapper/)
[![Changelog](https://img.shields.io/github/v/release/mse11/click-wrapper?include_prereleases&label=changelog)](https://github.com/mse11/click-wrapper/releases)
[![Tests](https://github.com/mse11/click-wrapper/actions/workflows/test.yml/badge.svg)](https://github.com/mse11/click-wrapper/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/mse11/click-wrapper/blob/master/LICENSE)

Automatic Python wrapper generator for Click CLI applications. Generate type-safe dataclasses and wrapper methods from Click command introspection

## Acknowledgments

Code inspiration based on [LLM](https://github.com/simonw/llm) by Simon Willison. 

Simon creates powerful CLI tools, but I wanted better Python API integration for programmatic use. 
While you can always use `subprocess` to access CLI, this wrapper approach provides a more Pythonic interface with type safety and IDE support
— at least that's what works better for me! 😊

## Installation

Install this tool using `pip`:
```bash
pip install click-wrapper
```

Install this tool using `uv`:
```bash
uv pip install click-wrapper
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

1.a) using 'uv' (preffered)

```bash
cd click-wrapper
uv sync --all-extras

source .venv/bin/activate       # on Linux/Mac
source .venv/Scripts/activate   # on Windows Gitbash
```

1.b) using 'venv'
```bash
cd click-wrapper
python -m venv .venv

source .venv/bin/activate       # on Linux/Mac
source .venv/Scripts/activate   # on Windows Gitbash
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```

2. To run the tests:
```bash
python -m pytest
```
