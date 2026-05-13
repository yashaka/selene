#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_NAME="${TINYMCE_IMAGE_NAME:-selene/tinymce-local}"
IMAGE_TAG="${TINYMCE_IMAGE_TAG:-latest}"
TINYMCE_VERSION="${TINYMCE_VERSION:-8.0.2}"

echo "Building ${IMAGE_NAME}:${IMAGE_TAG} with tinymce@${TINYMCE_VERSION}"
docker build \
  --build-arg TINYMCE_VERSION="${TINYMCE_VERSION}" \
  -t "${IMAGE_NAME}:${IMAGE_TAG}" \
  "${ROOT_DIR}"
