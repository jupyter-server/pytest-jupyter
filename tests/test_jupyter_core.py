import os

from jupyter_core import paths


def test_environ(jp_environ):
    assert os.path.exists(paths.jupyter_data_dir())
