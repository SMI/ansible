#!/usr/bin/env python3
import argparse
import glob
import hashlib
import json
import os
import shutil
import sys
import tarfile
import tempfile
import urllib.request


def main() -> int:

    parser = argparse.ArgumentParser()
    parser.add_argument("base_url")
    parser.add_argument("install_root")
    parser.add_argument("versions", type=json.loads)
    args = parser.parse_args()

    for version, version_data in args.versions.items():

        install_dir = f"{args.install_root}/v{version}"

        if os.path.isdir(install_dir):
            print(f"{install_dir} already exists")
            return 0
        os.mkdir(install_dir)

        with tempfile.TemporaryDirectory() as tempdir:
            for p in version_data["packages"]:
                if not p["checksum"].startswith("sha256:"):
                    print(
                        f"Checksum format not supported: {p['checksum']}",
                        file=sys.stderr,
                    )
                    return 1

                package_name = p["name"].replace("<VERSION>", version)
                url = f"{args.base_url}/v{version}/{package_name}"
                package_path = f"{tempdir}/{package_name}"
                urllib.request.urlretrieve(url, filename=package_path)

                expected_sha256 = p["checksum"].split(":")[1]
                with open(package_path, "rb") as fd:
                    file_sha256 = hashlib.sha256(fd.read()).hexdigest().upper()
                if expected_sha256 != file_sha256:
                    err = (
                        f"Checksum error. "
                        f"Expected {expected_sha256}, got {file_sha256}"
                    )
                    print(err, file=sys.stderr)
                    return 1

                package_ext = package_path.split(".")[-1]
                if package_ext == "xz":
                    with tarfile.open(package_path) as tar:
                        tar.extractall(tempdir)
                if "file_blocklist" not in p:
                    continue

                unpacked_dir = glob.glob(f"{tempdir}/{p['name'].split('<')[0]}*/")
                assert (
                    len(unpacked_dir) == 1
                ), f"glob matched multiple files: {unpacked_dir}"
                for blocked in p["file_blocklist"]:
                    for f in glob.glob(
                        f"{unpacked_dir[0]}/**/{blocked}",
                        recursive=True,
                    ):
                        os.remove(f)

            rdmp_cli_dir = glob.glob(f"{tempdir}/rdmp-*/")
            assert (
                len(rdmp_cli_dir) == 1
            ), f"glob matched multiple files: {rdmp_cli_dir}"
            shutil.copytree(rdmp_cli_dir[0], f"{install_dir}/rdmp-cli")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
