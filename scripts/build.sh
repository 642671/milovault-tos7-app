#!/bin/sh
# Build the TOS 7 Docker application archive and its SHA-256 checksum.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
PYTHON=${PYTHON:-python3}

"$PYTHON" scripts/validate.py

rm -rf dist
mkdir -p dist/pkg
cp config.ini milovault.lang milovault.svg docker-compose.yml dist/pkg/
(
    cd dist/pkg
    tar -czf ../milovault.tar.gz \
        config.ini milovault.lang milovault.svg docker-compose.yml
)
rm -rf dist/pkg

if command -v sha256sum >/dev/null 2>&1; then
    ( cd dist && sha256sum milovault.tar.gz > milovault.tar.gz.sha256 )
else
    ( cd dist && shasum -a 256 milovault.tar.gz > milovault.tar.gz.sha256 )
fi

"$PYTHON" scripts/validate.py --package dist/milovault.tar.gz

echo "Built:"
ls -lh dist/
cat dist/milovault.tar.gz.sha256
