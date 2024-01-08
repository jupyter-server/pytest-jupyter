import os

os.environ["JUPYTER_PLATFORM_DIRS"] = "1"
pytest_plugins = [
    "pytest_jupyter",
    "pytest_jupyter.jupyter_server",
    "pytest_jupyter.jupyter_client",
]
