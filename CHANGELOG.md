# Changelog

## 1.0.1

- Fix the clean-install restart loop: a small `milovault-init` helper prepares
  `/data` ownership for UID/GID 10001, then drops to `nobody` and stays healthy
  for the platform. The main container waits until `/data` is writable instead
  of crash-looping.
- Make certificate generation verifiable and idempotent (expiry and key/cert
  match are checked before reuse; a replacement is generated atomically).
- Escape shell `$` as `$$` in the compose command blocks so Compose does not
  substitute runtime variables before the container starts; the init container
  now handles SIGTERM and exits 0, and certificate generation logs a clear
  error if OpenSSL fails.
- Disable website icon downloading (`DISABLE_ICON_DOWNLOAD=true`,
  `ICON_CACHE_TTL=0`) so the only outbound request made by the package is the
  Docker Hub image pull.
- Tighten permissions: package files are 0644 root-owned, `UMASK=0077` is set,
  `/data` and `/data/certs` are 0700, and the private key and database files are
  0600. The main container drops all capabilities and enables
  `no-new-privileges`.
- Add a complete privacy policy, point `help` at it, align the description in
  all 14 languages with the delivered web vault, and remove the beta flag.

## 1.0.0

- Initial TOS 7 Docker application package.
- Vaultwarden 1.37.5 from Docker Hub.
- Host port 18443, container port 8443.
- Runtime-generated self-signed certificate for first boot.
- Non-root container (`10001:10001`), health check, `unless-stopped`.
