#!/bin/bash

python setup.py sdist

twine upload --skip-existing dist/*

rm -rf dist

echo "Current source uploaded to PyPi"

