[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/SMI/ansible/main.svg)](https://results.pre-commit.ci/latest/github/SMI/ansible/main)

# Ansible

⚠ This repo is in early development ⚠

Automated deployment of the SMI software stack.

The roles in this collection can be used to deploy the following software to a remote target:

- [SmiServices](https://github.com/SMI/SmiServices)
- [IsIdentifiable](https://github.com/SMI/IsIdentifiable)
- [RDMP CLI](https://github.com/HicServices/RDMP)

## Requirements

- Python 3.10

## Usage

The `site.yaml` playbook will deploy all configured software to the host(s) in the `software_host` group of your inventory. This can be overridden through the `target` variable e.g., `ansible-playbook ... -e "target=localhost" site.yaml`.

Included in the repo are two convenience scripts to execute this playbook without an inventory.

### Local

```console
$ ./bin/local-deploy
```

will execute the playbook with the install directory set to `~/opt/epcc/smi`.

### Docker

_WIP_

```console
$ ./bin/build-docker-aio
```

will launch a docker image and execute the playbook against it. If the playbook
succeeds, the image will be saved and tagged as `smi/aio:latest`.

### Docker Services

Also included are scripts to start/stop containers with the services we depend
on (e.g., MongoDB):

```console
$ ./bin/start-docker-services
...
$ ./bin/stop-docker-services
```

## Developing

Please see the [CONTRIBUTING](CONTRIBUTING.md) guide to get started.
