import argparse
import os
import subprocess
import sys

INSTALL_DIR = "{{ smi_service_software_install_dir }}"
FILE_LOAD_CONFIG = "file_load_services.yaml"
FILE_EXTRACT_CONFIG = "file_extract_services.yaml"


def _env_from(file_path: str) -> dict[str, str]:
    env = {}
    with open(file_path) as f:
        for line in f.read().splitlines():
            if not line.startswith("export"):
                continue
            var, val = line.split(" ", 1)[1].split("=")
            env[var] = val.strip('"')
    return env


def init() -> tuple[argparse.Namespace, dict[str, str], str]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--detach", action="store_true")
    parser.add_argument("--copies", type=int, default=1)
    wrapper_args = parser.parse_args()

    if wrapper_args.copies > 1:
        wrapper_args.detach = True

    assert "SMI_ENV" in os.environ, "SMI_ENV must be set"
    smi_env = os.environ["SMI_ENV"]
    env_dir = f"{INSTALL_DIR}/configs/{smi_env}"
    assert os.path.isdir(env_dir), f"{env_dir} does not exist"
    env = {**os.environ, **_env_from(f"{env_dir}/env.bash")}

    if not wrapper_args.quiet:
        for var in sorted(x for x in env if x.startswith("SMI_")):
            print(f"{var}={env[var]}")

    config_dir = f"{INSTALL_DIR}/configs/{smi_env}"

    return (wrapper_args, env, config_dir)


def run(
    wrapper_args: argparse.Namespace,
    cmd: tuple[str, ...],
    env: dict[str, str],
) -> None:
    if not wrapper_args.quiet:
        print(f"Executing {wrapper_args.copies}x:")
        subprocess.check_call(("echo", "$", *cmd))

    if wrapper_args.detach:
        for _ in range(wrapper_args.copies):
            subprocess.Popen(
                cmd,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    else:
        try:
            subprocess.check_call(
                cmd,
                env=env,
            )
        except KeyboardInterrupt:
            pass


def run_smiservices(config_name: str, single_instance: bool = False) -> None:
    wrapper_args, env, config_dir = init()

    if wrapper_args.copies > 1 and single_instance:
        raise ValueError("Cannot start more than one copy of this service")

    config_path = os.path.join(config_dir, config_name)
    smi_bin = (
        f"{INSTALL_DIR}/software/SmiServices/v{env['SMI_SMISERVICES_VERSION']}/smi/smi"
    )
    app_name = sys.argv[0].split("smi-")[1].split(".py")[0]
    cmd = (smi_bin, app_name, "-y", config_path)
    run(wrapper_args, cmd, env)
