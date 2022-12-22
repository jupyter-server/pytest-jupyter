"""Utilities for pytest-jupyter."""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.


def mkdir(tmp_path, *parts):
    """Make a directory given extra path parts."""
    path = tmp_path.joinpath(*parts)
    if not path.exists():
        path.mkdir(parents=True)
    return path
