# pytest-jupyter

A set of [pytest plugins](https://docs.pytest.org/en/stable/plugins.html) for Jupyter libraries and extensions.

## Basic Usage

Install `pytest-jupyter` from PyPI using pip:
```
pip install pytest-jupyter
```

Once it's installed, all fixtures from `pytest-jupyter` will be discoverable by Pytest. Pass any fixture to your unit test function to begin using it, like so:

```python
async def test_jupyter_server_api(jp_fetch):
    # Send request to a temporary Jupyter Server Web Application
    response = await jp_fetch("api/spec.yml")

    # Confirm that the request is successful.
    assert response.code == 200
```


```{toctree}
:maxdepth: 2
:hidden:

Core <plugins/jupyter_core>
Server <plugins/jupyter_server>

```

## Search

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
