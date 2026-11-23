# MiloVault Privacy Policy

Last updated: 2026-11-23

MiloVault is a TerraMaster TOS 7 packaging wrapper for the open-source
[Vaultwarden](https://github.com/dani-garcia/vaultwarden) server. The package
runs on the user's own NAS. The publisher does not operate a MiloVault service,
does not receive vault contents, and does not collect telemetry or analytics.

## Scope

This policy covers the MiloVault Docker package distributed through the
TerraMaster App Center and this repository. It does not cover third-party
Bitwarden clients, browsers, or other applications that users choose to connect
to their own Vaultwarden server.

## Data you store

The vault stores the data the user creates in Vaultwarden: the encrypted vault
database (`db.sqlite3`), RSA key material (`rsa_key.pem`), attachments, sends,
icons, the generated TLS certificate and private key, and local logs. The
publisher has no access to these files.

## Where data is stored

All persistent data stays on the NAS in the application data directory:

```
/Volume<N>/DockerAppData/milovault/data/
```

The directory is bind-mounted into the container at `/data`. No vault data is
uploaded to the publisher or to a cloud service. The package itself contacts
Docker Hub only to pull `vaultwarden/server:1.37.5` and `alpine:3.20`. Website
icon fetching is disabled, and push notifications are disabled, so the
Vaultwarden service does not make third-party requests on the user's behalf.

## Retention

Data is retained on the NAS until the user deletes it. There is no automatic
expiry, and the publisher keeps no copy. Uninstalling MiloVault from the App
Center without selecting "delete data" intentionally keeps
`/Volume<N>/DockerAppData/milovault/` so that a reinstall can reuse the vault.
Selecting "delete data" during uninstall removes the same directory. Local
backups are controlled entirely by the user and are retained according to the
user's own backup policy.

## User rights

The user can access and export vault items from the Vaultwarden web vault,
correct entries there, and delete individual items or the whole vault. Because
the publisher never receives the data, requests to the publisher cannot reveal
or restore vault contents; the NAS administrator controls the files and the
Vaultwarden configuration.

## Deletion

To delete all MiloVault data, uninstall the application in the TOS App Center
and enable the "delete data" option, or remove
`/Volume<N>/DockerAppData/milovault/` from the NAS. Deleting the container or
the application directory without the data directory leaves the vault in place.
Users should also clear any downloaded copies and browser caches on their
clients. The deletion channel is the TOS App Center uninstall flow or the NAS
file manager/SSH access controlled by the administrator.

## Security measures

- The web interface is served over HTTPS. The first start generates a
  self-signed certificate, so browsers warn until the user accepts or replaces
  it with a trusted certificate.
- The main container runs as UID/GID `10001:10001`, drops all Linux
  capabilities, and enables `no-new-privileges`.
- A helper container prepares ownership of the data directory, then drops to
  `nobody` for an idle health process; it has no network ports and retains only
  `CHOWN`, `DAC_OVERRIDE`, `FOWNER`, `SETUID`, and `SETGID` for its lifetime.
- Files are created with `UMASK=0077`; the data and certificate directories are
  mode 0700, and the private key and database are mode 0600.
- Vaultwarden encrypts vault items with keys derived from the user's master
  password. The NAS administrator and anyone with root access to the device can
  still copy the database and key material, so disk encryption, strong
  administrator credentials, and encrypted backups are recommended.

## Third-party sharing

The publisher does not sell, rent, or share vault data with third parties and
does not include advertising, analytics, or tracking SDKs. Docker Hub (Docker,
Inc.) serves the container images and may log standard registry requests; see
its own privacy policy. Vaultwarden push notifications and website icon
fetching are disabled in the shipped configuration. Bitwarden browser
extensions, mobile apps, and the `bw` CLI are optional third-party clients
operated by their respective projects.

## International transfers

MiloVault does not transfer vault data across borders. Image downloads from
Docker Hub may be served from infrastructure outside the user's country; that
transfer contains registry request metadata, not vault contents.

## Children

MiloVault is a general-purpose password manager and is not directed at
children. The administrator is responsible for who may access the NAS and the
vault.

## Changes

Material changes to this policy will be published in this repository and in the
release notes of the affected version. The policy shipped with a version is the
one that applies to that version.

## Contact

Questions or privacy requests can be opened at
<https://github.com/642671/milovault-tos7-app/issues>. Because the publisher
does not hold vault data, data-access and deletion requests must be performed on
the NAS by its administrator.
