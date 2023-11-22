[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/SMI/playbook/main.svg)](https://results.pre-commit.ci/latest/github/SMI/playbook/main)

# SMI Playbook

⚠ This repo is in early development ⚠

Automated deployment of the SMI software stack.

## Requirements

-   Python 3.10

## Usage

The `site.yaml` file contains a playbook which can deploy to a provided
inventory.

Included in the repo are two convenience methods to execute the playbook without
an inventory.

### Local

```console
$ ./bin/local-deploy
```

will execute the playbook with the install directory set to `~/opt/epcc/smi`.

You may also need to add your system to the supported list, e.g.:

```diff
--- a/roles/00-preflight/defaults/main.yml
+++ b/roles/00-preflight/defaults/main.yml
@@ -4,3 +4,4 @@ smi_preflight_allow_create_group: false

 smi_preflight_supported_systems:
   - "Ubuntu-22.04"
+  - "Rocky-9.3"
```

### Docker

```console
$ ./bin/build-docker-aio
```

will launch a docker image and execute the playbook against it. If the playbook
succeeds, the image will be saved and tagged as `smi/aio:latest`.

## Developing

Please see the [CONTRIBUTING](CONTRIBUTING.md) guide to get started.
