#!/usr/bin/env bash

set -euxo pipefail

IMAGE="smi/aio"
CONTAINER_NAME="${IMAGE/\//_}_build"

docker build --pull --tag "${IMAGE}:build" .

docker kill "${CONTAINER_NAME}" || true
docker run --rm -d --name "${CONTAINER_NAME}" "${IMAGE}:build"

ansible \
    --connection docker \
    --inventory "${CONTAINER_NAME}," \
    --extra-vars \
        ansible_python_interpreter=python3.10 \
    -m ping \
    all

# run ansible

docker commit "${CONTAINER_NAME}" "${IMAGE}:latest"
docker kill "${CONTAINER_NAME}"
