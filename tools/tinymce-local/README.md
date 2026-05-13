# TinyMCE local demo for tests

This folder contains a self-hosted TinyMCE demo used by integration tests.

## Why

The old remote page (`https://autotest.how/demo/tinymce`) can become read-only because of Tiny Cloud load limits. This setup provides a deterministic local endpoint for both CI and local runs.

## What it serves

- Demo URL: `http://127.0.0.1:8000/demo/tinymce`
- Health URL: `http://127.0.0.1:8000/health`

## Quick start (local)

```bash
./tools/tinymce-local/scripts/run.sh
```

Stop:

```bash
./tools/tinymce-local/scripts/stop.sh
```

## Configuration

Optional environment variables:

- `TINYMCE_VERSION` (default: `8.0.2`)
- `TINYMCE_IMAGE_NAME` (default: `selene/tinymce-local`)
- `TINYMCE_IMAGE_TAG` (default: `latest`)
- `TINYMCE_CONTAINER_NAME` (default: `selene-tinymce-local`)
- `TINYMCE_HOST_PORT` (default: `8000`)

## CI usage

GitHub Actions starts the same container and uses the same URL, so tests do not need separate local/CI configuration.
