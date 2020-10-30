# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import jupyter_core.paths
import os
import pytest
import shutil
import sys

from .utils import mkdir


@pytest.fixture
def jp_home_dir(tmp_path):
    """Provides a temporary HOME directory value."""
    return mkdir(tmp_path, "home")


@pytest.fixture
def jp_data_dir(tmp_path):
    """Provides a temporary Jupyter data dir directory value."""
    return mkdir(tmp_path, "data")


@pytest.fixture
def jp_config_dir(tmp_path):
    """Provides a temporary Jupyter config dir directory value."""
    return mkdir(tmp_path, "config")


@pytest.fixture
def jp_runtime_dir(tmp_path):
    """Provides a temporary Jupyter runtime dir directory value."""
    return mkdir(tmp_path, "runtime")


@pytest.fixture
def jp_system_jupyter_path(tmp_path):
    """Provides a temporary Jupyter system path value."""
    return mkdir(tmp_path, "share", "jupyter")


@pytest.fixture
def jp_env_jupyter_path(tmp_path):
    """Provides a temporary Jupyter env system path value."""
    return mkdir(tmp_path, "env", "share", "jupyter")


@pytest.fixture
def jp_system_config_path(tmp_path):
    """Provides a temporary Jupyter config path value."""
    return mkdir(tmp_path, "etc", "jupyter")


@pytest.fixture
def jp_env_config_path(tmp_path):
    """Provides a temporary Jupyter env config path value."""
    return mkdir(tmp_path, "env", "etc", "jupyter")


@pytest.fixture
def jp_environ(
    monkeypatch,
    tmp_path,
    jp_home_dir,
    jp_data_dir,
    jp_config_dir,
    jp_runtime_dir,
    jp_system_jupyter_path,
    jp_system_config_path,
    jp_env_jupyter_path,
    jp_env_config_path,
):
    """Configures a temporary environment based on Jupyter-specific environment variables. """
    monkeypatch.setenv("HOME", str(jp_home_dir))
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join(sys.path))

    # Get path to nbconvert template directory *before*
    # monkeypatching the paths env variable.
    possible_paths = jupyter_core.paths.jupyter_path('nbconvert', 'templates')
    nbconvert_path = None
    for path in possible_paths:
        if os.path.exists(path):
            nbconvert_path = path
            break

    nbconvert_target = jp_data_dir / 'nbconvert' / 'templates'

    # monkeypatch.setenv("JUPYTER_NO_CONFIG", "1")
    monkeypatch.setenv("JUPYTER_CONFIG_DIR", str(jp_config_dir))
    monkeypatch.setenv("JUPYTER_DATA_DIR", str(jp_data_dir))
    monkeypatch.setenv("JUPYTER_RUNTIME_DIR", str(jp_runtime_dir))
    monkeypatch.setattr(
        jupyter_core.paths, "SYSTEM_JUPYTER_PATH", [str(jp_system_jupyter_path)]
    )
    monkeypatch.setattr(jupyter_core.paths, "ENV_JUPYTER_PATH", [str(jp_env_jupyter_path)])
    monkeypatch.setattr(
        jupyter_core.paths, "SYSTEM_CONFIG_PATH", [str(jp_system_config_path)]
    )
    monkeypatch.setattr(jupyter_core.paths, "ENV_CONFIG_PATH", [str(jp_env_config_path)])

    # copy nbconvert templates to new tmp data_dir.
    if nbconvert_path:
        shutil.copytree(nbconvert_path, str(nbconvert_target))
