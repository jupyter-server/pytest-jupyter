# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import os
import pytest
import shutil
import sys

import jupyter_core.paths


def mkdir(tmp_path, *parts):
    path = tmp_path.joinpath(*parts)
    if not path.exists():
        path.mkdir(parents=True)
    return path


jp_home_dir = pytest.fixture(lambda tmp_path: mkdir(tmp_path, "home"))
jp_data_dir = pytest.fixture(lambda tmp_path: mkdir(tmp_path, "data"))
jp_config_dir = pytest.fixture(lambda tmp_path: mkdir(tmp_path, "config"))
jp_runtime_dir = pytest.fixture(lambda tmp_path: mkdir(tmp_path, "runtime"))
jp_root_dir = pytest.fixture(lambda tmp_path: mkdir(tmp_path, "root_dir"))
jp_template_dir = pytest.fixture(lambda tmp_path: mkdir(tmp_path, "templates"))
jp_system_jupyter_path = pytest.fixture(
    lambda tmp_path: mkdir(tmp_path, "share", "jupyter")
)
jp_env_jupyter_path = pytest.fixture(
    lambda tmp_path: mkdir(tmp_path, "env", "share", "jupyter")
)
jp_system_config_path = pytest.fixture(lambda tmp_path: mkdir(tmp_path, "etc", "jupyter"))
jp_env_config_path = pytest.fixture(
    lambda tmp_path: mkdir(tmp_path, "env", "etc", "jupyter")
)


@pytest.fixture
def jp_environ(
    monkeypatch,
    tmp_path,
    jp_home_dir,
    jp_data_dir,
    jp_config_dir,
    jp_runtime_dir,
    jp_root_dir,
    jp_system_jupyter_path,
    jp_system_config_path,
    jp_env_jupyter_path,
    jp_env_config_path,
):
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
