#!/usr/bin/bash
poetry run python3.8 setup.py sdist bdist_wheel
poetry run twine upload dist/*