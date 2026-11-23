# MiloVault 1.0.1 submission notes

Status: **code and package prepared; local container E2E and TOS device runtime
regression passed on 2026-11-24**. TOS App Center manual upload accepts only
`.tpk`/`.deb`; Docker packages are installed from the store, and publishing to
the test store was explicitly out of scope for this run. The device regression
therefore used the platform-documented Docker install sequence against the
worst-case clean-install ownership state. See "TOS device regression" below.

## Review findings addressed

- **F2 clean-install restart loop**: the platform creates
  `/Volume<N>/DockerAppData/milovault/data` as root with mode 0755. A
  `milovault-init` helper (Alpine, no ports, read-only rootfs, only `CHOWN`,
  `DAC_OVERRIDE`, `FOWNER`, `SETUID`, and `SETGID`) now creates `/data/certs`
  and gives `/data` to 10001:10001. It then drops to `nobody`, keeps a health
  check green so the platform sees every service healthy, and exits 0 on
  SIGTERM. The main service depends on it and waits until `/data` is writable
  before starting, so a failed preparation produces a clear log line instead of
  a tight crash loop. Certificate generation checks expiry and the key/cert
  pair, is idempotent, and reports a clear error if OpenSSL fails.
  Shell variables in the compose command blocks are escaped as `$$`; without
  that, Compose substitutes them with empty strings before the container starts
  (found during local container E2E).
- **D16 relative mount ownership**: `./data:/data` is kept because it is the
  platform-supported DockerAppData path and is cleaned when the user selects
  "delete data". Its ownership is now prepared by the init service instead of
  assuming the platform chowns it.
- **C3/C4/C5 privacy policy**: added `docs/PRIVACY.md` covering retention,
  user rights, security measures, third-party sharing, and the deletion
  channel. The public URL is used as the `help` field:
  <https://github.com/642671/milovault-tos7-app/blob/main/docs/PRIVACY.md>.
- **C9/F5 description and functionality**: all 14 descriptions now describe the
  delivered web vault and Bitwarden-compatible API served at
  `https://<NAS-IP>:18443` with a self-signed certificate, instead of promising
  automatic extension/mobile/CLI support. The service now starts on a clean
  install, so the described web vault is usable.
- **S11 permissions**: package files are recorded as root:root 0644; the
  container uses `UMASK=0077`, `/data` and `/data/certs` are 0700, the private
  key and database are 0600, the main container runs as 10001:10001 with all
  capabilities dropped and `no-new-privileges`, and the init container has a
  read-only rootfs with only `CHOWN`, `DAC_OVERRIDE`, `FOWNER`, `SETUID`, and
  `SETGID`.
- **V11 beta marker**: `beta` is now `false` and the beta wording was removed
  from the README.

## Build

```sh
python3 scripts/validate.py
sh scripts/build.sh
```

Expected output:

```
dist/milovault.tar.gz
dist/milovault.tar.gz.sha256
```

The archive contains exactly `config.ini`, `milovault.lang`, `milovault.svg`,
and `docker-compose.yml`, with root:root ownership and mode 0644.

## Local container E2E (not a substitute for TOS device validation)

Date: 2026-11-23. Environment: Ubuntu 24.04 WSL2, Docker 29.1.3, Compose
2.40.3. The test reproduced the platform's clean-install ownership state: a
root:root 0755 `data` directory, then `docker compose up -d`.

- Both `milovault` and `milovault-init` reached `Up (healthy)` with
  `RestartCount=0`.
- Host data became `10001:10001`, mode 0700; `certs` was 0700; the private key,
  database, WAL/SHM files, and log were 0600; the certificate was 0644.
- Port 18443 was listening, `GET /` returned HTTP 200 with the Vaultwarden web
  vault, and `GET /alive` returned a timestamp.
- A container restart reused the same certificate and key (SHA-256 unchanged).
- `compose stop` stopped the service and closed the port; `compose start`
  returned both containers to healthy.
- `compose down` removed the containers and network but retained `data`;
  reinstalling reused the data and returned HTTP 200; deleting `data` removed
  the application data. `docker stop milovault-init` now exits 0 in under one
  second.

## TOS device regression (10.18.15.189)

Date: 2026-11-24. Device: TOS 7.0.1536, x86_64, Docker 29.4.0. The test used
the same sequence the platform documents for Docker installs
(`pull -> down -> create -> start`) from the extracted package, with the data
root deliberately left at the platform-created clean-install state:
`root:root 0755`.

- `milovault` and `milovault-init` both reached `running` with
  `RestartCount=0`; no restart loop, no permission errors in the main log.
- Port 18443 listened on IPv4/IPv6; `GET /` and `GET /alive` returned 200;
  `https://10.18.15.189:18443/` returned the Vaultwarden web vault.
- `/data` and `/data/certs` became `10001:10001 0700`; the key and database
  were `10001:10001 0600`; the certificate was `10001:10001 0644`.
- `compose stop` closed port 18443; `compose start` brought both containers
  back and the web vault returned 200.
- `compose down` removed both containers and the network but retained `/data`;
  reinstalling kept the same certificate and database SHA-256 (idempotent) and
  returned 200 again.
- A clean uninstall (`compose down` plus removing `DockerAppData/milovault`)
  left no containers or data; the temporary package and config directories were
  removed afterwards.

Platform-managed App Center install/stop/start/remove cannot be exercised with a
local Docker package: the App Center manual-install wizard accepts only
`.tpk`/`.deb`, and the test store was not used. The TDP review environment will
exercise that path with this release asset.

## Release

After device validation:

```sh
git tag v1.0.1
git push origin main --tags
gh release create v1.0.1 \
  dist/milovault.tar.gz dist/milovault.tar.gz.sha256 \
  --title "MiloVault 1.0.1" \
  --notes-file <release-notes.txt>
```

The App Center reads the version from `config.ini`, not from the tag.

## TDP submission

Use the personal token through `curl --config`; never print the token. Base URL:
`https://api-developer.terra-master.com`.

1. `GET /v1/whoami`.
2. `GET /v1/apps?kind=all` and locate the x86_64 entity for `milovault`.
3. Submit:

```json
{
  "tag": "v1.0.1",
  "browser_download_url": "https://github.com/642671/milovault-tos7-app/releases/download/v1.0.1/milovault.tar.gz"
}
```

4. Poll the task and check the Parse Result: name `MiloVault`, version `1.0.1`,
   architecture `x86_64`, size and SHA-256 matching the attached archive, and
   the full release note. Confirm only when all values match.

## Validation status

- Local: `python3 scripts/validate.py` and `sh scripts/build.sh` are run after
  every edit; the tar ownership/mode check is part of the validator. The local
  Docker E2E described above passed on 2026-11-23.
- Device: runtime regression passed on 10.18.15.189 (see above). The
  platform-managed App Center flow remains for the TDP review environment
  because local Docker packages cannot be uploaded through App Center.

## Known limitations

- The certificate is self-signed and cannot include the NAS IP, so browsers
  warn on first use. A trusted HTTPS reverse proxy is recommended for
  production.
- `DOMAIN` is `https://localhost:18443` because the platform does not inject the
  NAS IP into the compose environment. The web vault and normal client sync use
  the configured origin; WebAuthn may not work with an IP-based origin.
- Signups are enabled for the first account. Disable them afterwards.
- Docker applications do not support in-place platform upgrades; uninstall and
  reinstall, keeping data when prompted.
- No admin token is configured, so `/admin` is disabled by default.
- Website icon fetching is disabled for privacy; entries use Vaultwarden's
  fallback icons instead of fetching third-party favicons.
