# Submission notes

## 1. Prepare

```sh
python3 scripts/validate.py
sh scripts/build.sh
```

Expected output:

```
dist/milovault.tar.gz
dist/milovault.tar.gz.sha256
```

The archive must contain exactly `config.ini`, `milovault.lang`,
`milovault.svg`, and `docker-compose.yml`.

## 2. Public repository and release

The repository must be public. Create a tag and a GitHub Release, then attach
both files:

```sh
git tag v1.0.0
git push origin main --tags
gh release create v1.0.0 \
  dist/milovault.tar.gz dist/milovault.tar.gz.sha256 \
  --title v1.0.0 \
  --notes "MiloVault 1.0.0 Docker package"
```

The App Center platform reads the version from `config.ini`, not from the tag.

## 3. TerraMaster developer platform

1. Sign in at <https://developer.terra-master.com>.
2. Create an application:
   - Application ID: `milovault`
   - Package type: `Docker`
   - Architecture: `x86_64`
   - Repository URL: the public repository URL
3. Open **Version Management** → **Add Version**.
4. Select the Release and `milovault.tar.gz`.
5. Submit for review.

## 4. API alternative

Create an API token under **API Keys** with at least `app:write` and
`version:write` (adding `app:read` and `version:read` is useful). Store it in a
0600 file:

```sh
umask 077
printf '%s' '<token>' > "$HOME/.tdp_token"
```

Never commit it or pass it as a command-line argument. The API base URL is
`https://api-developer.terra-master.com`. The workflow is:

1. `GET /v1/whoami` — verify identity and scopes.
2. `GET /v1/apps` — find the App entity UUID by `app_id`.
3. `POST /v1/apps` — create the App if it does not exist:
   ```json
   {"app_id":"milovault","kind":"docker","platform":"x86_64","repo":"https://github.com/642671/milovault-tos7-app"}
   ```
4. `GET /v1/apps/{entity_uuid}/releases` — confirm the release asset URL.
5. `POST /v1/apps/{entity_uuid}/versions` with:
   ```json
   {"tag":"v1.0.0","browser_download_url":"https://github.com/642671/milovault-tos7-app/releases/download/v1.0.0/milovault.tar.gz"}
   ```
6. Poll `GET .../tasks/{task_id}` until `all_status` is `2`; inspect the
   `.../result`; only then `POST .../confirm`.

## 5. Known review risks

- The first-run certificate is self-signed and its SAN does not include the NAS
  IP. The App Center opens `https://${ip}:18443`, so the reviewer will see a
  certificate warning.
- Bitwarden's web vault requires a secure context; HTTPS is used, but the
  certificate is not trusted by default.
- Signups are enabled on first install.
- Docker apps cannot be upgraded in place; reviewers should test install,
  start, stop, and uninstall.
- The `DOMAIN` environment variable is `https://localhost:18443` because the
  platform does not inject the NAS IP into compose. Basic login/sync works;
  WebAuthn and some absolute links may not.

These are documented rather than hidden. If the review rejects the package for
the certificate issue, the next step is the Deb iframe variant, which uses the
TOS HTTPS proxy and `/var/api` socket instead of a self-signed certificate.

## 6. After submission

Delete the API token used for submission and create a new one if further
automation is needed.
