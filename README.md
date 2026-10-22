# ModX Revolution Docker

![Docker Build](https://github.com/749/docker-modx-revolution/actions/workflows/docker-publish.yml/badge.svg)
[![Docker Image Version](https://img.shields.io/docker/stars/g749/modx-revolution)](https://hub.docker.com/r/g749/modx-revolution)

A docker setup that can auto-update ModX Revolution.

_This is a heavily modified version of the FPM variant of [the official Docker Image](https://github.com/modxcms/docker-modx)._

## Simplified Usage

1. Copy the `.env.example` file to `.env`
2. Run `docker compose up -d`
3. The Webserver will now listen on Ports `80` and `443`

The Compose example uses MODX 3 and MariaDB 13. On a fresh start, wait for
`docker compose logs -f modx_php` to report a completed MODX installation before
opening the site.

### Upgrading an existing Compose installation

These image changes upgrade both the application and database across major
versions. Back up the database and the `modx_config`, `modx_packages`,
`modx_components`, and `modx_assets` volumes before updating. For example, while
the old stack is running, create a logical database backup:

```sh
mkdir -p ../modx-backups
docker compose exec -T modx_mysql sh -c 'exec mariadb-dump --single-transaction -u"$MARIADB_USER" -p"$MARIADB_PASSWORD" "$MARIADB_DATABASE"' > ../modx-backups/modx.sql
```

Keep an offline copy of the named volumes as well, then stop the stack with
`docker compose down` (without `-v`). After updating the Compose file, start it
with `docker compose pull && docker compose up -d`. The MariaDB image runs its
system-table upgrade on the existing data volume, and the MODX entrypoint runs
the MODX upgrade installer. Check `docker compose logs modx_mysql modx_php` and
test the site and installed extras before resuming normal use. If an upgrade
fails, restore the database and volume backups before starting the old image
versions again; changing tags alone cannot undo a data migration.

MariaDB 13 is a rolling release. Review the [MariaDB upgrade
guidance](https://mariadb.com/docs/server/server-management/install-and-upgrade-mariadb/upgrading/mariadb-community-server-upgrade-paths/general-upgrade-information)
and [MODX 3 upgrade
guide](https://docs.modx.com/3.x/en/getting-started/upgrading-to-3.0) for
application-specific compatibility changes.

## General

The build runs every Sunday at 00:00 UTC. It selects the highest stable patch in the highest minor release of every MODX major version starting with 2, then builds each one with the latest stable PHP FPM Alpine image.

To publish all major lines manually, select **Actions → Docker Build → Run workflow** and choose `main`. Pushes to `main` also update all major lines; the newest major additionally gets `edge`.

It pulls in the latest version of ModX Revolution, based on the tags on the [Modx Revolution Tags](https://github.com/modxcms/revolution/tags).

Each build publishes its full version, minor, and major tags. For example, MODX `2.8.9` is published as `2.8.9`, `2.8`, and `2`. The newest major version also gets `latest`.

Older minor lines within a major version are not built. For example, a new `2.7` patch will not update the image when `2.8` is the latest minor line. See [#1](https://github.com/749/docker-modx-revolution/issues/1).

## Support

The image is created for the following platforms:

I only use arm64 and amd64 so those are actively tested. Support for the others may be dropped if the build proves to difficult to maintain.

<!-- prettier-ignore -->
| Platform     | Support |
| ------------ | ------- |
| linux/amd64  | ✅      |
| linux/arm64  | ✅      |
| linux/arm/v7 | ❓      |
| linux/386    | ❌      |
| linux/arm/v6 | ❌      |
