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
import zipfile


def main() -> int:

    parser = argparse.ArgumentParser()
    parser.add_argument("base_url")
    parser.add_argument("install_root")
    parser.add_argument("versions", type=json.loads)
    args = parser.parse_args()

    rc = 0
    for version, version_data in args.versions.items():

        install_dir = f"{args.install_root}/v{version}"

        if os.path.isdir(install_dir):
            print(f"{install_dir} already exists")
            continue
        os.mkdir(install_dir)

        with tempfile.TemporaryDirectory() as tempdir:
            for p in version_data["packages"]:
                if not p["checksum"].startswith("md5:"):
                    print(
                        f"Checksum format not supported: {p['checksum']}",
                        file=sys.stderr,
                    )
                    return 2

                package_name = p["name"].replace("<VERSION>", version)
                url = f"{args.base_url}/v{version}/{package_name}"
                package_path = f"{tempdir}/{package_name}"
                urllib.request.urlretrieve(url, filename=package_path)

                expected_md5 = p["checksum"].split(":")[1]
                with open(package_path, "rb") as fd:
                    file_md5 = hashlib.md5(fd.read()).hexdigest()
                if expected_md5 != file_md5:
                    print(
                        f"Checksum error. Expected {expected_md5}, got {file_md5}",
                        file=sys.stderr,
                    )
                    return 2

                package_ext = package_path.split(".")[-1]
                if package_ext == "tgz":
                    with tarfile.open(package_path) as tar:
                        tar.extractall(tempdir)
                elif package_ext == "zip":
                    with zipfile.ZipFile(package_path) as zip:
                        zip.extractall(tempdir)
                else:
                    continue

                if "file_blocklist" not in p:
                    continue

                unpacked_dir = glob.glob(f"{tempdir}/{p['name'].split('<')[0]}*/")
                assert (
                    len(unpacked_dir) == 1
                ), f"Expected only one match: {unpacked_dir}"
                for blocked in p["file_blocklist"]:
                    for f in glob.glob(
                        f"{unpacked_dir[0]}/**/{blocked}",
                        recursive=True,
                    ):
                        os.remove(f)

            # Copy SmiServices
            smiservices_dir = glob.glob(f"{tempdir}/smi-services*/")
            assert (
                len(smiservices_dir) == 1
            ), f"Expected only one match: {smiservices_dir}"
            shutil.copytree(smiservices_dir[0], f"{install_dir}/smi")

            # Copy CTPAnonymiser
            ctp_jar = f"{tempdir}/ctpanonymiser-1.0.0/CTPAnonymiser-portable-1.0.0.jar"
            shutil.copy2(ctp_jar, f"{install_dir}/CTPAnonymiser.jar")

            print(f"Deployed v{version}")
            rc = 1

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
