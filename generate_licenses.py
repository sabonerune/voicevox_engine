import json
import os
import subprocess
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class License:
    name: str
    version: Optional[str]
    license: Optional[str]
    text: str


def generate_licenses() -> List[License]:
    licenses: List[License] = []

    # openjtalk
    # https://sourceforge.net/projects/open-jtalk/files/Open%20JTalk/open_jtalk-1.11/
    licenses.append(
        License(
            name="Open JTalk",
            version="1.11",
            license="Modified BSD license",
            text=Path("docs/licenses/open_jtalk/COPYING").read_text(),
        )
    )
    licenses.append(
        License(
            name="MeCab",
            version=None,
            license="Modified BSD license",
            text=Path("docs/licenses/open_jtalk/mecab/COPYING").read_text(),
        )
    )
    licenses.append(
        License(
            name="NAIST Japanese Dictionary",
            version=None,
            license="Modified BSD license",
            text=Path("docs/licenses//open_jtalk/mecab-naist-jdic/COPYING").read_text(),
        )
    )

    # OpenJVox Engine
    # FIXME: リリースしたらURLにする
    licenses.append(
        License(
            name="OpenJVox Engine",
            version=None,
            license="LGPL license",
            text=Path("LGPL_LICENSE").read_text(encoding="utf-8"),
        )
    )

    # VOICEVOX ENGINE
    with urllib.request.urlopen(
        "https://raw.githubusercontent.com/VOICEVOX/voicevox_engine/master/LGPL_LICENSE"
    ) as res:
        licenses.append(
            License(
                name="VOICEVOX ENGINE",
                version=None,
                license="LGPL license",
                text=res.read().decode(),
            )
        )

    # world
    with urllib.request.urlopen(
        "https://raw.githubusercontent.com/mmorise/World/master/LICENSE.txt"
    ) as res:
        licenses.append(
            License(
                name="world",
                version=None,
                license="Modified BSD license",
                text=res.read().decode(),
            )
        )

    # Python
    python_version = "3.8.10"
    with urllib.request.urlopen(
        f"https://raw.githubusercontent.com/python/cpython/v{python_version}/LICENSE"
    ) as res:
        licenses.append(
            License(
                name="Python",
                version=python_version,
                license="Python Software Foundation License",
                text=res.read().decode(),
            )
        )

    # pip
    try:
        pip_licenses_output = subprocess.run(
            "pip-licenses "
            "--from=mixed "
            "--format=json "
            "--with-urls "
            "--with-license-file "
            "--no-license-path ",
            shell=True,
            capture_output=True,
            check=True,
            env=os.environ,
        ).stdout.decode()
    except subprocess.CalledProcessError as err:
        raise Exception(
            f"command output:\n{err.stderr and err.stderr.decode()}"
        ) from err

    licenses_json = json.loads(pip_licenses_output)
    for license_json in licenses_json:
        license = License(
            name=license_json["Name"],
            version=license_json["Version"],
            license=license_json["License"],
            text=license_json["LicenseText"],
        )
        # FIXME: assert license type
        if license.text == "UNKNOWN":
            if license.name.lower() == "core" and license.version == "0.0.0":
                continue
            elif license.name.lower() == "future":
                with urllib.request.urlopen(
                    "https://raw.githubusercontent.com/PythonCharmers/python-future/master/LICENSE.txt"  # noqa: B950
                ) as res:
                    license.text = res.read().decode()
            elif license.name.lower() == "pefile":
                with urllib.request.urlopen(
                    "https://raw.githubusercontent.com/erocarrera/pefile/master/LICENSE"  # noqa: B950
                ) as res:
                    license.text = res.read().decode()
            elif license.name.lower() == "pyopenjtalk":
                with urllib.request.urlopen(
                    "https://raw.githubusercontent.com/r9y9/pyopenjtalk/master/LICENSE.md"
                ) as res:
                    license.text = res.read().decode()
            elif license.name.lower() == "python-multipart":
                with urllib.request.urlopen(
                    "https://raw.githubusercontent.com/andrew-d/python-multipart/master/LICENSE.txt"  # noqa: B950
                ) as res:
                    license.text = res.read().decode()
            elif license.name.lower() == "romkan":
                with urllib.request.urlopen(
                    "https://raw.githubusercontent.com/soimort/python-romkan/master/LICENSE"
                ) as res:
                    license.text = res.read().decode()
            elif license.name.lower() == "distlib":
                with urllib.request.urlopen(
                    "https://bitbucket.org/pypa/distlib/raw/7d93712134b28401407da27382f2b6236c87623a/LICENSE.txt"  # noqa: B950
                ) as res:
                    license.text = res.read().decode()
            elif license.name.lower() == "jsonschema":
                with urllib.request.urlopen(
                    "https://raw.githubusercontent.com/python-jsonschema/jsonschema/dbc398245a583cb2366795dc529ae042d10c1577/COPYING"
                ) as res:
                    license.text = res.read().decode()
            elif license.name.lower() == "lockfile":
                with urllib.request.urlopen(
                    "https://opendev.org/openstack/pylockfile/raw/tag/0.12.2/LICENSE"
                ) as res:
                    license.text = res.read().decode()
            elif license.name.lower() == "platformdirs":
                with urllib.request.urlopen(
                    "https://raw.githubusercontent.com/platformdirs/platformdirs/aa671aaa97913c7b948567f4d9c77d4f98bfa134/LICENSE"
                ) as res:
                    license.text = res.read().decode()
            elif license.name.lower() == "webencodings":
                with urllib.request.urlopen(
                    "https://raw.githubusercontent.com/gsnedders/python-webencodings/fa2cb5d75ab41e63ace691bc0825d3432ba7d694/LICENSE"
                ) as res:
                    license.text = res.read().decode()
            else:
                # ライセンスがpypiに無い
                raise Exception(f"No License info provided for {license.name}")
        licenses.append(license)

    # OpenBLAS
    with urllib.request.urlopen(
        "https://raw.githubusercontent.com/xianyi/OpenBLAS/develop/LICENSE"
    ) as res:
        licenses.append(
            License(
                name="OpenBLAS",
                version=None,
                license="BSD 3-clause license",
                text=res.read().decode(),
            )
        )

    return licenses


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_path", type=str)
    args = parser.parse_args()

    output_path = args.output_path

    licenses = generate_licenses()

    # dump
    out = Path(output_path).open("w") if output_path else sys.stdout
    json.dump(
        [asdict(license) for license in licenses],
        out,
    )
