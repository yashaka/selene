#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_NAME="${TINYMCE_IMAGE_NAME:-selene/tinymce-local}"
IMAGE_TAG="${TINYMCE_IMAGE_TAG:-latest}"
CONTAINER_NAME="${TINYMCE_CONTAINER_NAME:-selene-tinymce-local}"
HOST_PORT="${TINYMCE_HOST_PORT:-8000}"

"${ROOT_DIR}/scripts/build.sh"

if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}$"; then
  docker rm -f "${CONTAINER_NAME}" >/dev/null
fi

docker run -d \
  --name "${CONTAINER_NAME}" \
  -p "${HOST_PORT}:8000" \
  "${IMAGE_NAME}:${IMAGE_TAG}" >/dev/null

for _ in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:${HOST_PORT}/health" >/dev/null; then
    echo "TinyMCE local demo is ready at http://127.0.0.1:${HOST_PORT}/demo/tinymce"
    exit 0
  fi
  sleep 1
done

echo "TinyMCE local demo failed to start" >&2
docker logs "${CONTAINER_NAME}" || true
exit 1
