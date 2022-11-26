# Releasing

First, bump the version to final release version.

Then follow these steps (which expect a Bash shell; they might not work with other shells).

```
git clean -dffx
pip install -q 517
python -m pep517.build .
export script_version=`python -c "from pytest_jupyter._version import __version__; print(__version__)"`
git commit -a -m "Release $script_version"
git tag $script_version
git push --all
git push --tags
pip install twine
twine check dist/*
twine upload dist/*
```
