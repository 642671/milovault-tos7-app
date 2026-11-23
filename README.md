# MiloVault（钥匙匣）— TOS 7 Docker application package

This repository is the **public submission source** for the MiloVault Docker
application in the TerraMaster TOS 7 App Center. It contains only the four
files required by the Docker package specification plus build/validation
tooling and documentation.

## What it is

MiloVault runs [Vaultwarden](https://github.com/dani-garcia/vaultwarden) 1.37.5
in Docker. It serves the Vaultwarden web vault and a Bitwarden-compatible API at
`https://<nas-ip>:18443`. Bitwarden clients can connect to that URL after the
user accepts or replaces the self-signed certificate.

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
container. The main container runs as UID/GID `10001:10001`. A small
`milovault-init` helper prepares the ownership of the bind-mounted data
directory, then drops to `nobody` and stays healthy for the platform. The main
container waits until `/data` is writable instead of entering a restart loop.

## First run

1. Open `https://<nas-ip>:18443`.
2. The container generates a self-signed certificate at first start. The browser
   will show a certificate warning; review it and continue if you accept the
   risk for a LAN deployment.
3. Create the first account in the Vaultwarden web vault.
4. Disable signups after the account is created. Edit the installed compose file
   (or the environment) and set `SIGNUPS_ALLOWED=false`, then recreate the
   container.

The first start generates a new certificate only when the existing pair is
missing, expired, or does not match; a valid pair is reused across restarts.

## Data

Application data is stored under:

```
/Volume<N>/DockerAppData/milovault/data/
```

The compose mount is `./data:/data`, which the platform resolves to the path
above. The directory contains `db.sqlite3`, `rsa_key.pem`, attachments, and the
generated certificate. Uninstalling without selecting "delete data" keeps this
directory; reinstall reuses it. Selecting "delete data" during uninstall removes
it. The data directory is mode 0700, files are created with `UMASK=0077`, and
the private key and database are mode 0600.

**Backups must be encrypted.** A backup contains the database and
`rsa_key.pem`; anyone who obtains an unencrypted backup may be able to recover
vault contents.

## Security notice and limitations

- The first-run certificate is self-signed and does not contain the NAS IP, so
  browsers will warn about both the certificate authority and the hostname.
  This is not suitable for production without a trusted HTTPS reverse proxy.
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
- Website icon fetching is disabled (`DISABLE_ICON_DOWNLOAD=true`,
  `ICON_CACHE_TTL=0`); the package's only outbound request is the Docker Hub
  image pull.

## Privacy

The privacy policy is published at [docs/PRIVACY.md](docs/PRIVACY.md) and its
public URL is used for the `help` field in `config.ini`. The publisher does not
receive vault data; all persistent data remains under
`/Volume<N>/DockerAppData/milovault/` on the NAS.

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

The archive records root:root ownership and mode 0644 for all four files. The
main container drops all capabilities, enables `no-new-privileges`, and the
init container keeps only `CHOWN`, `DAC_OVERRIDE`, `FOWNER`, `SETUID`, and
`SETGID`; it drops to `nobody` after the ownership step and handles SIGTERM.

Compose interpolates `$` in the compose file before the container starts, so
the shell snippets escape runtime variables as `$$`. `scripts/validate.py`
rejects any single-dollar shell reference to keep that behaviour from breaking
on a clean install.

The GitHub Actions workflow builds and attaches these assets when a `v*` tag is
pushed.

## Licenses

- This packaging repository: MIT (see `LICENSE`).
- Vaultwarden: GPL-3.0. The container image is pulled from Docker Hub and is not
  bundled in this repository.
- Bitwarden web vault assets are distributed inside the official Vaultwarden
  image; see the upstream project for their license terms.
