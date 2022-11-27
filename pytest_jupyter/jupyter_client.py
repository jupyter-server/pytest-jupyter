# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import json
import os
import sys
from pathlib import Path
from typing import Optional

import pytest
from jupyter_core import paths

try:
    import ipykernel
    import jupyter_client
except ImportError:
    import warnings

    warnings.warn(
        "The client plugin has not been installed. "
        "If you're trying to use this plugin and you've installed "
        "`pytest-jupyter`, there is likely one more step "
        "you need. Try: `pip install 'pytest-jupyter[client]'`"
    )

try:
    import resource
except ImportError:
    # Windows
    resource = None  # type: ignore


# Handle resource limit
# Ensure a minimal soft limit of DEFAULT_SOFT if the current hard limit is at least that much.
if resource is not None:
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)

    DEFAULT_SOFT = 4096
    if hard >= DEFAULT_SOFT:
        soft = DEFAULT_SOFT

    if hard < soft:
        hard = soft

    resource.setrlimit(resource.RLIMIT_NOFILE, (soft, hard))


@pytest.fixture
def zmq_context():
    import zmq

    ctx = zmq.asyncio.Context()
    yield ctx
    ctx.term()


@pytest.fixture
async def start_kernel(kernel_spec):
    from jupyter_client.client import KernelClient
    from jupyter_client.manager import AsyncKernelManager, start_new_async_kernel

    km = None
    kc = None

    async def inner(kernel_name="echo", **kwargs):
        nonlocal km, kc
        km, kc = await start_new_async_kernel(kernel_name=kernel_name, **kwargs)
        return km, kc

    yield inner

    if kc and km:
        kc.stop_channels()
        await km.shutdown_kernel(now=True)
        assert km.context.closed


@pytest.fixture()
def kernel_dir():
    return os.path.join(paths.jupyter_data_dir(), "kernels")


@pytest.fixture
def kernel_spec(kernel_dir):
    test_dir = Path(kernel_dir) / "echo"
    test_dir.mkdir(parents=True, exist_ok=True)
    argv = [sys.executable, "-m", "pytest_jupyter.echo_kernel", "-f", "{connection_file}"]
    kernel_data = {"argv": argv, "display_name": "echo", "language": "echo"}
    spec_file_path = Path(test_dir / "kernel.json")
    spec_file_path.write_text(json.dumps(kernel_data), "utf8")
    return str(test_dir)
