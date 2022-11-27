def test_zmq_context(zmq_context):
    assert isinstance(zmq_context.underlying, int)


async def test_start_kernel(start_kernel):
    km, _ = await start_kernel()
    assert km.kernel_name == "echo"
