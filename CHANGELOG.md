# Changelog

## 1.0.0

- Initial TOS 7 Docker application package.
- Vaultwarden 1.37.5 from Docker Hub.
- Host port 18443, container port 8443.
- Runtime-generated self-signed certificate for first boot.
- Non-root container (`10001:10001`), health check, `unless-stopped`.
