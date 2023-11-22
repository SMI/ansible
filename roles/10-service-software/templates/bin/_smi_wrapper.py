import argparse
import functools
import os
import subprocess
import sys

FILE_LOAD_CONFIG = "file_load_services.yaml"
FILE_EXTRACT_CONFIG = "file_extract_services.yaml"

_INSTALL_DIR = "{{ smi_service_software_install_dir }}"


def _env_from(file_path: str) -> dict[str, str]:
    env = {}
    with open(file_path) as f:
        for line in f.read().splitlines():
            if not line.startswith("export"):
                continue
            var, val = line.split(" ", 1)[1].split("=")
            env[var] = val.strip('"')
    return env


def run_smiservices(config: str) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--detach", action="store_true")
    parser.add_argument("--copies", type=int, default=1)
    args = parser.parse_args()

    if args.copies > 1:
        args.detach = True

    assert "SMI_ENV" in os.environ, "SMI_ENV must be set"
    smi_env = os.environ["SMI_ENV"]
    env_dir = f"{_INSTALL_DIR}/configs/{smi_env}"
    assert os.path.isdir(env_dir), f"{env_dir} does not exist"
    env = {**os.environ, **_env_from(f"{env_dir}/env.bash")}

    if not args.quiet:
        for var in sorted(x for x in env if x.startswith("SMI_")):
            print(f"{var}={env[var]}")

    smi_bin = (
        f"{_INSTALL_DIR}/software/SmiServices/v{env['SMI_SMISERVICES_VERSION']}/smi/smi"
    )
    app_name = sys.argv[0].split("smi-")[1].split(".py")[0]
    config = f"{_INSTALL_DIR}/configs/{smi_env}/{config}"
    cmd = (smi_bin, app_name, "-y", config)

    if not args.quiet:
        subprocess.check_call(("echo", "$", *cmd))

    check_call = subprocess.check_call
    if args.detach:
        check_call = functools.partial(
            subprocess.check_call,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    for _ in range(args.copies):
        check_call(cmd, env=env)

    return 0
