"""Vendored fork of pytest_tornasync from
  https://github.com/eukaryote/pytest-tornasync/blob/9f1bdeec3eb5816e0183f975ca65b5f6f29fbfbb/src/pytest_tornasync/plugin.py
"""
from contextlib import closing
from inspect import iscoroutinefunction

try:
    import tornado.ioloop
    import tornado.testing
    from tornado.simple_httpclient import SimpleAsyncHTTPClient
except ImportError:
    SimpleAsyncHTTPClient = object  # type:ignore[assignment,misc]

import pytest

# mypy: disable-error-code="no-untyped-call"


@pytest.hookimpl(tryfirst=True)
def pytest_pycollect_makeitem(collector, name, obj):
    """Custom pytest collection hook."""
    if collector.funcnamefilter(name) and iscoroutinefunction(obj):
        return list(collector._genfunctions(name, obj))
    return None


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    """Custom pytest function call hook."""
    funcargs = pyfuncitem.funcargs
    testargs = {arg: funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames}

    if not iscoroutinefunction(pyfuncitem.obj):
        pyfuncitem.obj(**testargs)
        return True

    try:
        loop = funcargs["io_loop"]
    except KeyError:
        loop = tornado.ioloop.IOLoop.current()

    loop.run_sync(lambda: pyfuncitem.obj(**testargs))
    return True


@pytest.fixture()
def http_server_port():
    """
    Port used by `http_server`.
    """
    return tornado.testing.bind_unused_port()


@pytest.fixture()
def http_server_client(http_server, io_loop):
    """
    Create an asynchronous HTTP client that can fetch from `http_server`.
    """

    async def get_client():
        """Get a client."""
        return AsyncHTTPServerClient(http_server=http_server)

    client = io_loop.run_sync(get_client)
    with closing(client) as context:
        yield context


class AsyncHTTPServerClient(SimpleAsyncHTTPClient):
    """An async http server client."""

    def initialize(self, *, http_server=None):
        """Initialize the client."""
        super().initialize()
        self._http_server = http_server

    def fetch(self, path, **kwargs):
        """
        Fetch `path` from test server, passing `kwargs` to the `fetch`
        of the underlying `SimpleAsyncHTTPClient`.
        """
        return super().fetch(self.get_url(path), **kwargs)

    def get_protocol(self):
        """Get the protocol for the client."""
        return "http"

    def get_http_port(self):
        """Get a port for the client."""
        for sock in self._http_server._sockets.values():
            return sock.getsockname()[1]
        return None

    def get_url(self, path):
        """Get the url for the client."""
        return f"{self.get_protocol()}://127.0.0.1:{self.get_http_port()}{path}"
