from unittest.mock import Mock

from jupyter_client.session import Session

from pytest_jupyter.echo_kernel import EchoKernel


def test_zmq_context(jp_zmq_context):
    assert isinstance(jp_zmq_context.underlying, int)


async def test_start_kernel(jp_start_kernel):
    km, kc = await jp_start_kernel("echo")
    assert km.kernel_name == "echo"
    msg = await kc.execute("hello", reply=True)
    assert msg["content"]["status"] == "ok"

    km, kc = await jp_start_kernel()
    assert km.kernel_name == "python3"
    msg = await kc.execute("print('hi')", reply=True)
    assert msg["content"]["status"] == "ok"


def test_echo_kernel():
    kernel = EchoKernel()  # type:ignore[no-untyped-call]
    kernel.session = Mock(spec=Session)
    kernel.do_execute("foo", False)
