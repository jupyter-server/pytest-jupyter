# pytest-jupyter

A set of pytest plugins for Jupyter libraries and extensions.

## Basic Usage

First, install `pytest-jupyter` from PyPI using pip:

```bash
pip install pytest-jupyter
```

This installs the basic pytest-jupyter package that includes fixture definitions for the various Jupyter-based pytest plugins.

To use one of these plugins, you'll also need to install their dependencies. This requires a second `pip install` call. For example, if you'd like to use the `jupyter_server` plugin, you'll need to call:

```bash
pip install "pytest-jupyter[server]"
```

This *should* install everything you need for the plugin to work.

To use a plugin, add it to the `pytest_plugins` list in the `conftest.py` of your project's root test directory.

```python
# inside the conftest.py

pytest_plugins = ["pytest_jupyter.jupyter_server"]
```

All fixtures inside the plugin (e.g. jupyter_server) will be available to all of your project's unit tests. You can use a fixtures by passing it as an argument to your unit test function:

```python
async def test_jupyter_server_api(jp_fetch):
    # Send request to a temporary Jupyter Server Web Application
    response = await jp_fetch("api/spec.yml")

    # Confirm that the request is successful.
    assert response.code == 200
```

You can list the fixtures for a given plugin using the `--fixtures` argument from the pytest command line interface:

```bash
pytest --fixtures -p pytest_jupyter.jupyter_server
```

or by calling the `pytest --fixtures` where the plugin is listed in the `pytest_plugins` variable of a given test directory.
