# jsonnetify

```bash
touch manifest.libsonnet
docker run --rm -it \
    -v $(pwd)/manifest.libsonnet:/work/manifest.libsonnet:z \
    ghcr.io/cloudflightio/jsonnetify:main \
    https://github.com/cert-manager/cert-manager/releases/download/v1.9.1/cert-manager.yaml
```