# MiloVault（钥匙匣）— TOS 7 Docker application package

This repository is the **public submission source** for the MiloVault Docker
application in the TerraMaster TOS 7 App Center. It contains only the four
files required by the Docker package specification plus build/validation
tooling and documentation.

## What it is

MiloVault runs [Vaultwarden](https://github.com/dani-garcia/vaultwarden) 1.37.5
in Docker. Vaultwarden is a Bitwarden-compatible server, so Bitwarden browser
extensions, mobile apps, and the `bw` CLI can log in and sync.

The package is intentionally small: the platform pulls the official
`vaultwarden/server:1.37.5` image from Docker Hub.

## Package contents

```
config.ini
milovault.lang
milovault.svg
docker-compose.yml
```

Plus `scripts/` for local validation/building and `docs/` for submission notes.
The release asset is `milovault.tar.gz` with exactly the four files above, and
`milovault.tar.gz.sha256`.

## Install

### From the App Center

After the version is published, install MiloVault from the TOS App Center. The
platform installs DockerEngine if needed and starts the container.

### Manual

```sh
tar -xzf milovault.tar.gz -C /path/to/milovault
cd /path/to/milovault
docker compose up -d
```

The app listens on host port **18443** and maps to port 8443 inside the
container. The container runs as UID/GID `10001:10001`; the platform chowns the
application data directory to that UID.

## First run

1. Open `https://<nas-ip>:18443`.
2. The container generates a self-signed certificate at first start. The browser
   will show a certificate warning; review it and continue if you accept the
   risk for a LAN deployment.
3. Create the first account in the Vaultwarden web vault.
4. Disable signups after the account is created. Edit the installed compose file
   (or the environment) and set `SIGNUPS_ALLOWED=false`, then recreate the
   container.

## Data

Application data is stored under:

```
/Volume<N>/DockerAppData/milovault/data/
```

The compose mount is `./data:/data`, which the platform resolves to the path
above. The directory contains `db.sqlite3`, `rsa_key.pem`, attachments, and the
generated certificate. Uninstalling without selecting "delete data" keeps this
directory; reinstall reuses it.

**Backups must be encrypted.** A backup contains the database and
`rsa_key.pem`; anyone who obtains an unencrypted backup may be able to recover
vault contents.

## Security notice and limitations

- This is a **beta** Docker package. The first-run certificate is self-signed
  and does not contain the NAS IP, so browsers will warn about both the
  certificate authority and the hostname. This is not suitable for production
  without a trusted HTTPS reverse proxy.
- The web UI is opened by the App Center in a new tab (`open_path: true`), not
  proxied through TOS. Use a trusted reverse proxy (for example Tailscale Serve)
  for real remote access.
- Vaultwarden's `DOMAIN` is set to `https://localhost:18443` because the
  platform does not inject the NAS IP into the compose environment. Basic login
  and sync use the current origin; WebAuthn and some absolute links may not work
  correctly.
- Docker applications do **not** support in-place platform upgrades. To upgrade,
  uninstall and reinstall; application data is retained unless explicitly
  deleted.
- Signups are enabled on first install by design. Disable them after creating
  the first account.
- No admin token is configured, so the Vaultwarden `/admin` page is disabled by
  default. Use the compose file to change settings.

## Build and validate

Requires Python 3 and a POSIX shell.

```sh
python3 scripts/validate.py
sh scripts/build.sh
```

`scripts/build.sh` produces:

```
dist/milovault.tar.gz
dist/milovault.tar.gz.sha256
```

The GitHub Actions workflow builds and attaches these assets when a `v*` tag is
pushed.

## Licenses

- This packaging repository: MIT (see `LICENSE`).
- Vaultwarden: GPL-3.0. The container image is pulled from Docker Hub and is not
  bundled in this repository.
- Bitwarden web vault assets are distributed inside the official Vaultwarden
  image; see the upstream project for their license terms.
