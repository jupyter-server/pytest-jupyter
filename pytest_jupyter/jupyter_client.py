# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import json
import os
import sys
from pathlib import Path

import pytest
from jupyter_core import paths

try:
    import ipykernel  # noqa
    from jupyter_client.manager import start_new_async_kernel
except ImportError:
    import warnings

    warnings.warn(
        "The client plugin has not been installed. "
        "If you're trying to use this plugin and you've installed "
        "`pytest-jupyter`, there is likely one more step "
        "you need. Try: `pip install 'pytest-jupyter[client]'`"
    )

from pytest_jupyter import *  # noqa

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
def start_kernel(echo_kernel_spec, asyncio_loop):
    kms = []
    kcs = []

    async def inner(kernel_name="echo", **kwargs):
        km, kc = await start_new_async_kernel(kernel_name=kernel_name, **kwargs)
        kms.append(km)
        kcs.append(kc)
        return km, kc

    yield inner

    for kc in kcs:
        kc.stop_channels()

    for km in kms:
        asyncio_loop.run_until_complete(km.shutdown_kernel(now=True))
        assert km.context.closed


@pytest.fixture()
def kernel_dir():
    return os.path.join(paths.jupyter_data_dir(), "kernels")


@pytest.fixture
def echo_kernel_spec(kernel_dir):
    test_dir = Path(kernel_dir) / "echo"
    test_dir.mkdir(parents=True, exist_ok=True)
    argv = [sys.executable, "-m", "pytest_jupyter.echo_kernel", "-f", "{connection_file}"]
    kernel_data = {"argv": argv, "display_name": "echo", "language": "echo"}
    spec_file_path = Path(test_dir / "kernel.json")
    spec_file_path.write_text(json.dumps(kernel_data), "utf8")
    return str(test_dir)
