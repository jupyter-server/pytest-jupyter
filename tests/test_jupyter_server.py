from jupyter_server.serverapp import ServerApp


def test_serverapp(jp_serverapp):
    assert isinstance(jp_serverapp, ServerApp)
