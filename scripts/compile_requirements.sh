#!/bin/bash
set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR/.."

# --universal + --python-version 3.11: resolve one set of pins valid for every
# Python in the CI matrix (3.11 up to 3.15), instead of only the local interpreter.
PIP_COMPILE_ARGS="-q --no-header --strip-extras --universal --python-version 3.11 --no-emit-options --no-emit-trusted-host --no-emit-find-links"

echo "Compiling requirements.txt..."
uv pip compile $PIP_COMPILE_ARGS -o "$SCRIPT_DIR/../requirements.txt" pyproject.toml
echo " └Done"

echo "Compiling requirements-dev.txt..."
uv pip compile $PIP_COMPILE_ARGS --extra dev -o "$SCRIPT_DIR/../requirements-dev.txt" pyproject.toml
echo " └Done"

cd -
