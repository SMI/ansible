[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/SMI/playbook/main.svg)](https://results.pre-commit.ci/latest/github/SMI/playbook/main)

# SMI Playbook

⚠ This repo is in early development ⚠

Automated deployment of the SMI software stack.

## Requirements

-   Python 3.10

## Usage

### Ansible

TBC

### Docker

This repo contains a script which can be used to build an AIO ("all-in-one")
Docker image of the SMI software stack. This does not include any dependent
services such as RabbitMQ however.

Run `./bin/build-docker-aio` to build the image locally. This may take some time
to build.

## Developing

Please see the [CONTRIBUTING](CONTRIBUTING.md) guide to get started.
