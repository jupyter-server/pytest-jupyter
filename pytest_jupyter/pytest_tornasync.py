# Vendored fork of pytest_tornasync from
# https://github.com/eukaryote/pytest-tornasync/blob/9f1bdeec3eb5816e0183f975ca65b5f6f29fbfbb/src/pytest_tornasync/plugin.py

from contextlib import closing
from inspect import iscoroutinefunction

try:
    import tornado.ioloop
    import tornado.testing
    from tornado.simple_httpclient import SimpleAsyncHTTPClient
except ImportError:
    SimpleAsyncHTTPClient = object

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_pycollect_makeitem(collector, name, obj):
    if collector.funcnamefilter(name) and iscoroutinefunction(obj):
        return list(collector._genfunctions(name, obj))


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    funcargs = pyfuncitem.funcargs
    testargs = {arg: funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames}

    if not iscoroutinefunction(pyfuncitem.obj):
        pyfuncitem.obj(**testargs)
        return True

    try:
        loop = funcargs["jp_io_loop"]
    except KeyError:
        loop = tornado.ioloop.IOLoop.current()

    loop.run_sync(
        lambda: pyfuncitem.obj(**testargs)
    )
    return True


@pytest.fixture
def jp_http_server_port():
    """
    Port used by `http_server`.
    """
    return tornado.testing.bind_unused_port()


@pytest.fixture
def jp_http_server_client(jp_http_server, jp_io_loop):
    """
    Create an asynchronous HTTP client that can fetch from `http_server`.
    """

    async def get_client():
        return AsyncHTTPServerClient(http_server=jp_http_server)

    client = jp_io_loop.run_sync(get_client)
    with closing(client) as context:
        yield context



class AsyncHTTPServerClient(SimpleAsyncHTTPClient):
    def initialize(self, *, http_server=None):
        super().initialize()
        self._http_server = http_server

    def fetch(self, path, **kwargs):
        """
        Fetch `path` from test server, passing `kwargs` to the `fetch`
        of the underlying `SimpleAsyncHTTPClient`.
        """
        return super().fetch(self.get_url(path), **kwargs)

    def get_protocol(self):
        return "http"

    def get_http_port(self):
        for sock in self._http_server._sockets.values():
            return sock.getsockname()[1]

    def get_url(self, path):
        return "%s://127.0.0.1:%s%s" % (self.get_protocol(), self.get_http_port(), path)
