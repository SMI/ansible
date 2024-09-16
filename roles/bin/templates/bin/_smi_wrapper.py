# {{ ansible_managed }}
import argparse
import os
import subprocess
import sys


assert "SMI_ROOT" in os.environ, "SMI_ROOT must be set"
smi_root = os.environ["SMI_ROOT"]

assert "SMI_ENV" in os.environ, "SMI_ENV must be set"
smi_env = os.environ["SMI_ENV"]

env_dir = f"{smi_root}/envs/{smi_env}"
assert os.path.isdir(env_dir), f"Expected {env_dir} to be a directory"

with open(f"{env_dir}/env.bash") as f:
    for line in f.read().splitlines():
        if not line.startswith("export"):
            continue
        var, val = line.split(" ", 1)[1].split("=")
        os.environ[var] = os.path.expandvars(val.strip('"'))


def init() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser()
    wrapper_group = parser.add_argument_group("Wrapper args")
    wrapper_group.add_argument("-v", "--verbose", action="store_true")
    wrapper_group.add_argument(
        "--detach",
        action="store_true",
        help="Launch service(s) in detached mode and exit",
    )
    wrapper_group.add_argument(
        "--copies",
        type=int,
        default=1,
        help=(
            "Launch multiple copies of the service. "
            "Implies --detached when value is greater than 1"
        ),
    )
    wrapper_args, remaining_argv = parser.parse_known_args()

    if wrapper_args.copies > 1:
        wrapper_args.detach = True

    return (wrapper_args, remaining_argv)


def print_smi_env() -> None:
    for var in sorted(x for x in os.environ if x.startswith("SMI_")):
        print(f"{var}={os.environ[var]}")


def run(
    wrapper_args: argparse.Namespace,
    remaining_argv: list[str],
    cmd: tuple[str, ...],
) -> None:
    cmd = (*cmd, *remaining_argv)

    if wrapper_args.verbose:
        print_smi_env()
        if wrapper_args.copies > 1:
            print(f"Executing {wrapper_args.copies} detached instances of:")
        subprocess.check_call(("echo", "$", *cmd))

    if wrapper_args.detach:
        for _ in range(wrapper_args.copies):
            subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    else:
        try:
            subprocess.check_call(cmd)
        except KeyboardInterrupt:
            pass


def run_smiservices(config_path: str, single_instance: bool = False) -> None:
    wrapper_args, remaining_argv = init()

    if (wrapper_args.copies > 1 or wrapper_args.detach) and single_instance:
        raise ValueError(
            "Cannot start more than one copy of this service, or run it detached",
        )

    smi_bin = os.environ["SMI_SMISERVICES_BIN"]
    app_name = sys.argv[0].rpartition("smi-")[-1]
    cmd = (smi_bin, app_name, "-y", config_path)
    run(wrapper_args, remaining_argv, cmd)
