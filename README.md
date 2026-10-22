# ModX Revolution Docker

![Docker Build](https://github.com/749/docker-modx-revolution/actions/workflows/docker-publish.yml/badge.svg)
[![Docker Image Version](https://img.shields.io/docker/stars/g749/modx-revolution)](https://hub.docker.com/r/g749/modx-revolution)

A docker setup that can auto-update ModX Revolution.

_This is a heavily modified version of the FPM variant of [the official Docker Image](https://github.com/modxcms/docker-modx)._

## Simplified Usage

1. Copy the `.env.example` file to `.env`
2. Run `docker-compose up`
3. The Webserver will now listen on Ports `80` and `443`

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
