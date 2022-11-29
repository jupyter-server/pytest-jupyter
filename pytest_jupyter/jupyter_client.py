# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import pytest

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

# Bring in local plugins.
from pytest_jupyter import *  # noqa
from pytest_jupyter.pytest_tornasync import *  # noqa


@pytest.fixture
def jp_zmq_context():
    import zmq

    ctx = zmq.asyncio.Context()
    yield ctx
    ctx.term()


@pytest.fixture
def jp_start_kernel(jp_environ, jp_asyncio_loop):
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
        jp_asyncio_loop.run_until_complete(km.shutdown_kernel(now=True))
        assert km.context.closed
