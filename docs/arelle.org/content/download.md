---
title: Download
description: Download Arelle for Windows, macOS and Linux.
aliases:
  - /arelle/pub/
---

## Desktop app

Choose the mirror closest to you. Each mirror serves the same current release.

| Build | Mirrors |
| --- | --- |
| Windows 64-bit installer | [US](https://arelle-us.s3-us-west-1.amazonaws.com/arelle-win.exe) · [Europe](https://arelle-eu.s3.eu-central-1.amazonaws.com/arelle-win.exe) · [Mainland China](https://arelle-cn.oss-cn-shenzhen.aliyuncs.com/arelle-win.exe) |
| Windows 64-bit zip | [US](https://arelle-us.s3-us-west-1.amazonaws.com/arelle-win.zip) · [Europe](https://arelle-eu.s3.eu-central-1.amazonaws.com/arelle-win.zip) · [Mainland China](https://arelle-cn.oss-cn-shenzhen.aliyuncs.com/arelle-win.zip) |
| macOS for Apple silicon | [US](https://arelle-us.s3-us-west-1.amazonaws.com/arelle-macos-arm64.dmg) · [Europe](https://arelle-eu.s3.eu-central-1.amazonaws.com/arelle-macos-arm64.dmg) · [Mainland China](https://arelle-cn.oss-cn-shenzhen.aliyuncs.com/arelle-macos-arm64.dmg) |
| macOS for Intel | [US](https://arelle-us.s3-us-west-1.amazonaws.com/arelle-macos-x64.dmg) · [Europe](https://arelle-eu.s3.eu-central-1.amazonaws.com/arelle-macos-x64.dmg) · [Mainland China](https://arelle-cn.oss-cn-shenzhen.aliyuncs.com/arelle-macos-x64.dmg) |
| Ubuntu Linux | [US](https://arelle-us.s3-us-west-1.amazonaws.com/arelle-ubuntu.tgz) · [Europe](https://arelle-eu.s3.eu-central-1.amazonaws.com/arelle-ubuntu.tgz) · [Mainland China](https://arelle-cn.oss-cn-shenzhen.aliyuncs.com/arelle-ubuntu.tgz) |

## Python and containers

### Python

Install the canonical Python package:

```shell
pip install arelle-release
```

See the [installation documentation](https://arelle.readthedocs.io/en/latest/install.html) for optional dependency groups and installation from source.

### Docker

Validate a local `filing.zip` from the current directory:

```shell
docker run --rm -v "$PWD:/data" arelleproject/arelle:latest \
  python arelleCmdLine.py --file /data/filing.zip --validate
```

Start Arelle as an HTTP web service on port 8080:

```shell
docker run --name arelle-webserver -p 8080:8080 \
  arelleproject/arelle:latest /opt/start.sh
```

See the [Docker installation documentation](https://arelle.readthedocs.io/en/latest/install.html#docker) for image variants, registries, Compose, custom images and output mounts.

For version numbers, release notes and older builds, see the [release history on GitHub](https://github.com/Arelle/Arelle/releases).
