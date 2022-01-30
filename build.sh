#!/bin/bash

set -e

REPOSITORY="alanmpinder/k8s-config-setup"

# We don't capture output so can see real-time progress
docker build --network=host .

# Docker sorts images by creation date, so the latest image is always the first
IID="$(docker images --format "{{ .ID }}" | head -1)"
IMAGE="${REPOSITORY}:${IID}"

echo "Image name: ${IMAGE}"

docker tag "${IID}" "${IMAGE}"
docker push "${IMAGE}"
