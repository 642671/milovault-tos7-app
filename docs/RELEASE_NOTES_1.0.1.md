# MiloVault 1.0.1

MiloVault packages Vaultwarden 1.37.5 for TerraMaster TOS 7 on x86_64.

## Fixes

- Clean installs no longer restart-loop when the platform creates
  `/Volume<N>/DockerAppData/milovault/data` as root with mode 0755. A
  `milovault-init` helper prepares `/data` for UID/GID 10001:10001 before the
  main container starts, then drops to `nobody` and stays healthy for the
  platform.
- Certificate generation checks expiry and the key/cert pair, generates a
  replacement atomically, and is reused across restarts.
- Compose shell variables are escaped as `$$` so Compose does not substitute
  them before the container starts; the init container handles SIGTERM and
  exits 0.
- Permissions are tightened: package files are root:root 0644, `/data` and
  `/data/certs` are 0700, and the private key, database, WAL/SHM files, and log
  are 0600. The main container runs as 10001:10001, drops all capabilities, and
  enables `no-new-privileges`.
- Added a complete privacy policy and pointed `help` at it.
- Aligned all 14 descriptions with the delivered web vault and
  Bitwarden-compatible API.
- Removed the beta marker and disabled website icon downloads
  (`DISABLE_ICON_DOWNLOAD=true`, `ICON_CACHE_TTL=0`).

## Install

Install MiloVault from the TOS App Center, then open
`https://<NAS-IP>:18443`. The first launch uses a self-signed certificate, so
the browser will warn; review and continue if you accept the risk for your LAN.
Create the first account, then disable signups.

Data stays under `/Volume<N>/DockerAppData/milovault/data/`. Uninstalling
without selecting "delete data" keeps the vault for a later reinstall.

## Notes

- The certificate does not include the NAS IP. Use a trusted HTTPS reverse
  proxy for production or remote access.
- `DOMAIN` is `https://localhost:18443` because the platform does not inject the
  NAS IP into the compose environment. The web vault and normal client sync use
  the origin you open; WebAuthn may not work with an IP-based origin.
- Docker applications do not support in-place platform upgrades. Uninstall and
  reinstall, keeping data when prompted.
- No admin token is configured, so `/admin` is disabled by default.
