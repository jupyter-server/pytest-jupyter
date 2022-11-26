# Jupyter Server plugin

The jupyter_server module provides fixtures for automatically setting-up/tearing-down Jupyter Servers.

To use this plugin, install the dependencies for this plugin:

```
pip install 'pytest-jupyter[server]'
```

and list the plugin in the `conftest.py` file at the root of your project's test directory.

You can make requests to a *test server* using the `jp_fetch` and `jp_ws_fetch` fixtures.

## Fixtures

```{eval-rst}
.. automodule:: pytest_jupyter.jupyter_server
    :members:
```
