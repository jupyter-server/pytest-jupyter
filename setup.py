
import pathlib
from setuptools import setup, find_packages

here = pathlib.Path('.')

readme_path = here.joinpath('README.md')
README = readme_path.read_text()
VERSION = "0.0.1"

setup(
    name="pytest-jupyter",
    packages=find_packages(),
    version=VERSION,
    description="A pytest plugin for testing Jupyter core libraries and extensions.",
    long_description=README,
    long_description_content_type='text/markdown',
    author='Jupyter Development Team',
    author_email='jupyter@googlegroups.com',
    url='http://jupyter.org',
    license='BSD',
    platforms="Linux, Mac OS X, Windows",
    keywords=['Jupyter', 'pytest'],
    # the following makes a plugin available to pytest
    entry_points={
        "pytest11": [
            "pytest-jupyterserver = pytest_jupyter.jupyter_server",
            "pytest-jupytercore = pytest_jupyter.jupyter_core"
        ]
    },
    # custom PyPI classifier for pytest plugins
    classifiers=["Framework :: Pytest"],
)
