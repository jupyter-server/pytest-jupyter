import asyncio
import os
import sys

# For backwards compatibility with older versions of server.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

os.environ["JUPYTER_PLATFORM_DIRS"] = "1"
pytest_plugins = [
    "pytest_jupyter",
    "pytest_jupyter.jupyter_server",
    "pytest_jupyter.jupyter_client",
]
