# ModX Revolution Docker

![Docker Build](https://github.com/749/docker-modx-revolution/actions/workflows/docker-publish.yml/badge.svg)

A docker setup that can auto-update ModX Revolution.

_This is a heavily modified version of the FPM variant of [the official Docker Image](https://github.com/modxcms/docker-modx)._

## Simplified Usage

1. Copy the `.env.example` file to `.env`
2. Run `docker-compose up`
3. The Webserver will now listen on Ports `80` and `443`

## General

The build is completely automated, running every sunday at 00:00/GMT+0.

It pulls in the latest 2.X version of ModX Revolution, based on the tags on the [Modx Revolution Tags](https://github.com/modxcms/revolution/tags).

The build produces convenience tags so `2.8.3` is also tagged `2.8` and `2`

**NOTE**: currently the build does not support building new versions for older minor tags. For Example the current minor is `2.8` and a new patch version commes out for `2.7`. A discussion issue is open at: [#1](https://github.com/749/docker-modx-revolution/issues/1)

## Support

The image is created for the following platforms, however I only use arm64 and amd64 so those are actively tested. Support for the others may be dropped if the build proves to difficult to maintain.

<!-- prettier-ignore -->
| Platform     | Support |
| ------------ | ------- |
| linux/amd64  | ✅      |
| linux/arm64  | ✅      |
| linux/arm/v7 | ❓      |
| linux/386    | ❌      |
| linux/arm/v6 | ❌      |
