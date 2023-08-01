#!/bin/bash

pip install build

# build the wheel and install it
WHEEL_NAME=$(python -m build | grep -Po "fastapi_oauth2-.*\.whl" | tail -n 1)
pip install dist/$WHEEL_NAME