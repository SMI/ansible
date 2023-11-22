# Contributing

TBC.

## Development Setup

Requirements are listed in `requirements.txt`. It's usually best to use a Python
virtual environment, e.g.:

```console
$ python3.10 -m venv venv
$ . venv/bin/activate
[venv] $ pip install --upgrade -r requirements.txt
...
```

To help ease integration with Ansible, we use the default Python version on the
target OS. For Ubuntu 22.04, this is Python 3.10.

### pre-commit

This repo uses [pre-commit](https://pre-commit.com) to install and automatically
run a series of linters and code formatters on each commit.

After cloning the repo and changing into the directory, run this command to
setup pre-commit:

```console
$ pip install --user pre-commit
$ pre-commit install
```

This will now run the checks each time you commit. It can also be run manually
at any time:

```console
$ pre-commit run [<hook>] (--all-files | --files <file list>)
```

See the link above for more information.

### Inventories

Local inventory files named with `inventory/test*` will be ignored by git.

Here are some sample inventory files to get started.

-   Azure VM:

    ```yaml
    [all:vars]
    ansible_ssh_user=<azure user>
    ansible_ssh_host=<public IP>
    ansible_ssh_private_key_file=<ssh key>

    ; Override variables
    smi_preflight_group_name=<group name>

    [service_software]
    azure ansible_host=<IP address> host_role="my test host"
    ```

-   EIDF VM:

    ```yaml
    [all:vars]
    ansible_ssh_user=<EIDF user>
    ansible_ssh_common_args="-J <EIDF user>@eidf-gateway.epcc.ed.ac.uk"
    ansible_ssh_pass="..."
    ansible_sudo_pass="..."

    ; Override variables
    smi_preflight_group_name=<group name>

    [service_software]
    eidf ansible_host=<IP address> host_role="my test host"
    ```

## Style Guide

-   Variable naming: `smi_<role-name>_...`
