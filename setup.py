
import pathlib
from setuptools import setup, find_packages
from jupyter_packaging import get_version

NAME = "pytest-jupyter"
PACKAGE_NAME = NAME.replace("-", "_")
DESCRIPTION = "A pytest plugin for testing Jupyter libraries and extensions."
VERSION = get_version(f"{PACKAGE_NAME}/_version.py")

HERE = pathlib.Path('.')
readme_path = HERE.joinpath('README.md')
README = readme_path.read_text()

setup_args = dict(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    author='Jupyter Development Team',
    author_email='jupyter@googlegroups.com',
    url='http://jupyter.org',
    license='BSD',
    platforms="Linux, Mac OS X, Windows",
    keywords=['Jupyter', 'pytest'],
    install_requires=[
        'traitlets',
        'tornado',
        'pytest',
        'nbformat',
        'pytest-tornasync',
        'jupyter_core',
        'jupyter_server'
    ],
    extras_require={
        'docs': ['Sphinx', 'myst_parser', 'pydata_sphinx_theme']
    },
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


if __name__ == '__main__':
    setup(**setup_args)

