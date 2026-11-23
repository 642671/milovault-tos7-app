#!/bin/sh
# Build the TOS 7 Docker application archive and its SHA-256 checksum.
set -eu

# Keep every packaged file world-readable but not writable/executable, and
# record root:root ownership in the archive (review item S11).
umask 022

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
PYTHON=${PYTHON:-python3}

"$PYTHON" scripts/validate.py

rm -rf dist
mkdir -p dist/pkg
cp config.ini milovault.lang milovault.svg docker-compose.yml dist/pkg/
chmod 0644 dist/pkg/config.ini dist/pkg/milovault.lang \
    dist/pkg/milovault.svg dist/pkg/docker-compose.yml
(
    cd dist/pkg
    tar --owner=0 --group=0 --numeric-owner --mode=0644 \
        --mtime="2024-01-01 00:00:00 UTC" \
        -czf ../milovault.tar.gz \
        config.ini milovault.lang milovault.svg docker-compose.yml
)
rm -rf dist/pkg

if command -v sha256sum >/dev/null 2>&1; then
    ( cd dist && sha256sum milovault.tar.gz > milovault.tar.gz.sha256 )
else
    ( cd dist && shasum -a 256 milovault.tar.gz > milovault.tar.gz.sha256 )
fi
chmod 0644 dist/milovault.tar.gz dist/milovault.tar.gz.sha256

"$PYTHON" scripts/validate.py --package dist/milovault.tar.gz

echo "Built:"
ls -lh dist/
cat dist/milovault.tar.gz.sha256
