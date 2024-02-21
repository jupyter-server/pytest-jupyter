import json
import os
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from jupyter_server.auth import Authorizer
from jupyter_server.serverapp import ServerApp
from tornado.websocket import WebSocketHandler

from pytest_jupyter.jupyter_server import _Authorizer

# mypy: ignore-errors


async def test_serverapp(jp_serverapp):
    assert isinstance(jp_serverapp, ServerApp)


def test_skip(jp_serverapp):
    pytest.skip("Forcing a skip")


async def test_get_api_spec(jp_fetch):
    response = await jp_fetch("api", "spec.yaml", method="GET")
    assert response.code == HTTPStatus.OK


async def test_send_request(send_request):
    code = await send_request("api/spec.yaml", method="GET")
    assert code == HTTPStatus.OK


async def test_connection(jp_fetch, jp_ws_fetch, jp_http_port, jp_auth_header):
    # Create kernel
    r = await jp_fetch("api", "kernels", method="POST", body="{}")
    kid = json.loads(r.body.decode())["id"]

    # Get kernel info
    r = await jp_fetch("api", "kernels", kid, method="GET")
    model = json.loads(r.body.decode())
    assert model["connections"] == 0

    # Open a websocket connection.
    ws = await jp_ws_fetch("api", "kernels", kid, "channels")
    ws.close()


async def test_authorizer(jp_server_authorizer, jp_serverapp, jp_base_url):
    auth: _Authorizer = jp_server_authorizer(parent=jp_serverapp)
    assert isinstance(auth, Authorizer)
    assert auth.normalize_url("foo") == "/foo"
    assert auth.normalize_url(f"{jp_base_url}/foo") == "/foo"
    request = MagicMock()
    request.method = "GET"
    request.path = "foo"
    handler = WebSocketHandler(jp_serverapp.web_app, request=request)
    assert not auth.is_authorized(handler, {}, "execute", None)
    assert auth.match_url_to_resource("/api/kernels") == "kernels"
    assert auth.match_url_to_resource("/api/shutdown") == "server"


async def test_create_notebook(jp_create_notebook):
    nb = jp_create_notebook("foo.ipynb")
    assert "nbformat" in nb


def test_template_dir(jp_template_dir):
    assert os.path.exists(jp_template_dir)


def test_extension_environ(jp_extension_environ):
    pass


def test_ioloop_fixture(io_loop):
    pass
