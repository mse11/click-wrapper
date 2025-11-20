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
Package is NOT under `pypi`, so you can simply install it via `uvx` (`uvx` will create temporary environment) 
```bash
uvx --with git+https://github.com/mse11/click-wrapper click-wrapper --help
```

## Usage
To be able to parse click application, you need to ensure following requirements (for all CLI subcommands):
* install `foo` package in your python environment
* provide path to module e.g. `foo.cli`, where `foo_main_cli_object` is defined 

For example, for `llm` package (created by Simon Willison) you can run:     
```bash
 uvx --with "llm>=0.27.1" --with git+https://github.com/mse11/click-wrapper click-wrapper export-help llm.cli cli
 uvx --with "llm>=0.27.1" --with git+https://github.com/mse11/click-wrapper click-wrapper export-wrapper llm.cli cli
 uvx --with "llm>=0.27.1" --with git+https://github.com/mse11/click-wrapper click-wrapper metadata llm.cli cli
```

<!---
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
-->

## Development

To contribute to this tool, checkout the code and create a new virtual environment:

### Development using 'uv' (preffered)

```bash
cd click-wrapper
uv sync --all-extras

source .venv/bin/activate       # on Linux/Mac
source .venv/Scripts/activate   # on Windows Gitbash
```
Run the tests:
```bash
pytest
```

### Development using 'venv' (alternative approach)
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

Run the tests:
```bash
python -m pytest
```
