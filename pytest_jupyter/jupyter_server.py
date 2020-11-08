# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import jupyter_core.paths
import nbformat
import os
import json
import pytest
import shutil
import tornado
import urllib.parse

from binascii import hexlify
from jupyter_server.extension import serverextension
from jupyter_server.serverapp import ServerApp
from jupyter_server.utils import url_path_join
from jupyter_server.services.contents.filemanager import FileContentsManager
from tornado.escape import url_escape
from traitlets.config import Config

from .utils import mkdir

# NOTE: This is a temporary fix for Windows 3.8
# We have to override the io_loop fixture with an
# asyncio patch. This will probably be removed in
# the future.
@pytest.fixture
def jp_asyncio_patch():
    """Appropriately configures the event loop policy if running on Windows w/ Python >= 3.8."""
    ServerApp()._init_asyncio_patch()


@pytest.fixture
def io_loop(jp_asyncio_patch):
    """Returns an ioloop instance that includes the asyncio patch for Windows 3.8 platforms."""
    loop = tornado.ioloop.IOLoop()
    loop.make_current()
    yield loop
    loop.clear_current()
    loop.close(all_fds=True)


@pytest.fixture
def jp_server_config():
    """Allows tests to setup their specific configuration values. """
    return {}


@pytest.fixture
def jp_root_dir(tmp_path):
    """Provides a temporary Jupyter root directory value."""
    return mkdir(tmp_path, "root_dir")


@pytest.fixture
def jp_template_dir(tmp_path):
    """Provides a temporary Jupyter templates directory value."""
    return mkdir(tmp_path, "templates")


@pytest.fixture
def jp_argv():
    """Allows tests to setup specific argv values. """
    return []


@pytest.fixture
def jp_extension_environ(jp_env_config_path, monkeypatch):
    """Monkeypatch a Jupyter Extension's config path into each test's environment variable"""
    monkeypatch.setattr(serverextension, "ENV_CONFIG_PATH", [str(jp_env_config_path)])


@pytest.fixture
def jp_http_port(http_server_port):
    """Returns the port value from the http_server_port fixture. """
    return http_server_port[-1]


@pytest.fixture
def jp_nbconvert_templates(jp_data_dir):
    """Setups up a temporary directory consisting of the nbconvert templates."""

    # Get path to nbconvert template directory *before*
    # monkeypatching the paths env variable via the jp_environ fixture.
    possible_paths = jupyter_core.paths.jupyter_path('nbconvert', 'templates')
    nbconvert_path = None
    for path in possible_paths:
        if os.path.exists(path):
            nbconvert_path = path
            break

    nbconvert_target = jp_data_dir / 'nbconvert' / 'templates'

    # copy nbconvert templates to new tmp data_dir.
    if nbconvert_path:
        shutil.copytree(nbconvert_path, str(nbconvert_target))


@pytest.fixture(scope='function')
def jp_configurable_serverapp(
    jp_nbconvert_templates,  # this fixture must preceed jp_environ
    jp_environ,
    jp_server_config,
    jp_argv,
    jp_http_port,
    tmp_path,
    jp_root_dir,
    io_loop,
):
    """Starts a Jupyter Server instance based on the provided configuration values."""
    ServerApp.clear_instance()

    def _configurable_serverapp(
        config=jp_server_config,
        argv=jp_argv,
        environ=jp_environ,
        http_port=jp_http_port,
        tmp_path=tmp_path,
        root_dir=jp_root_dir,
        **kwargs
    ):
        c = Config(config)
        c.NotebookNotary.db_file = ":memory:"
        token = hexlify(os.urandom(4)).decode("ascii")
        url_prefix = "/"
        app = ServerApp.instance(
            # Set the log level to debug for testing purposes
            log_level='DEBUG',
            port=http_port,
            port_retries=0,
            open_browser=False,
            root_dir=str(root_dir),
            base_url=url_prefix,
            config=c,
            allow_root=True,
            token=token,
            **kwargs
        )

        app.init_signal = lambda: None
        app.log.propagate = True
        app.log.handlers = []
        # Initialize app without httpserver
        app.initialize(argv=argv, new_httpserver=False)
        app.log.propagate = True
        app.log.handlers = []
        # Start app without ioloop
        app.start_app()
        return app

    return _configurable_serverapp


@pytest.fixture(scope="function")
def jp_serverapp(jp_server_config, jp_argv, jp_configurable_serverapp):
    """Starts a Jupyter Server instance based on the established configuration values."""
    app = jp_configurable_serverapp(config=jp_server_config, argv=jp_argv)
    yield app
    app.remove_server_info_file()
    app.remove_browser_open_file()
    app.cleanup_kernels()


@pytest.fixture
def app(jp_serverapp):
    """app fixture is needed by pytest_tornasync plugin"""
    return jp_serverapp.web_app


@pytest.fixture
def jp_auth_header(jp_serverapp):
    """Configures an authorization header using the token from the serverapp fixture."""
    return {"Authorization": "token {token}".format(token=jp_serverapp.token)}


@pytest.fixture
def jp_base_url():
    """Returns the base url to use for the test."""
    return "/"


@pytest.fixture
def jp_fetch(http_server_client, jp_auth_header, jp_base_url):
    """Performs an HTTP request against the test server."""
    def client_fetch(*parts, headers={}, params={}, **kwargs):
        # Handle URL strings
        path_url = url_escape(url_path_join(jp_base_url, *parts), plus=False)
        params_url = urllib.parse.urlencode(params)
        url = path_url + "?" + params_url
        # Add auth keys to header
        headers.update(jp_auth_header)
        # Make request.
        return http_server_client.fetch(
            url, headers=headers, request_timeout=20, **kwargs
        )
    return client_fetch


@pytest.fixture
def jp_ws_fetch(jp_auth_header, jp_http_port):
    """Performs a websocket request against the test server."""
    def client_fetch(*parts, headers={}, params={}, **kwargs):
        # Handle URL strings
        path = url_escape(url_path_join(*parts), plus=False)
        urlparts = urllib.parse.urlparse('ws://localhost:{}'.format(jp_http_port))
        urlparts = urlparts._replace(
            path=path,
            query=urllib.parse.urlencode(params)
        )
        url = urlparts.geturl()
        # Add auth keys to header
        headers.update(jp_auth_header)
        # Make request.
        req = tornado.httpclient.HTTPRequest(
            url,
            headers=jp_auth_header,
            connect_timeout=120
        )
        return tornado.websocket.websocket_connect(req)
    return client_fetch


some_resource = u"The very model of a modern major general"
sample_kernel_json = {
    'argv':['cat', '{connection_file}'],
    'display_name': 'Test kernel',
}
@pytest.fixture
def jp_kernelspecs(jp_data_dir):
    """Configures some sample kernelspecs in the Jupyter data directory."""
    spec_names = ['sample', 'sample 2']
    for name in spec_names:
        sample_kernel_dir = jp_data_dir.joinpath('kernels', name)
        sample_kernel_dir.mkdir(parents=True)
        # Create kernel json file
        sample_kernel_file = sample_kernel_dir.joinpath('kernel.json')
        sample_kernel_file.write_text(json.dumps(sample_kernel_json))
        # Create resources text
        sample_kernel_resources = sample_kernel_dir.joinpath('resource.txt')
        sample_kernel_resources.write_text(some_resource)


@pytest.fixture(params=[True, False])
def jp_contents_manager(request, jp_root_dir):
    """Returns a FileContentsManager instance based on the use_atomic_writing parameter value."""
    return FileContentsManager(root_dir=str(jp_root_dir), use_atomic_writing=request.param)


@pytest.fixture
def jp_create_notebook(jp_root_dir):
    """Creates a notebook in the test's home directory."""
    def inner(nbpath):
        nbpath = jp_root_dir.joinpath(nbpath)
        # Check that the notebook has the correct file extension.
        if nbpath.suffix != '.ipynb':
            raise Exception("File extension for notebook must be .ipynb")
        # If the notebook path has a parent directory, make sure it's created.
        parent = nbpath.parent
        parent.mkdir(parents=True, exist_ok=True)
        # Create a notebook string and write to file.
        nb = nbformat.v4.new_notebook()
        nbtext = nbformat.writes(nb, version=4)
        nbpath.write_text(nbtext)
    return inner
