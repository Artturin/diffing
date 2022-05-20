"""
usage:
    diffing ".#bash"
"""

import argparse
import json
import os
import subprocess
import textwrap
from pathlib import Path


def is_strict_already(attr: str, nixgits: Path) -> bool:
    """check if strictDeps is enabled already"""
    strict_nixpkgs = Path(f"{nixgits}/my-nixpkgs")
    os.chdir(strict_nixpkgs)
    strict_deps_status = (
        subprocess.check_output(
            [
                "nix",
                "eval",
                "--impure",
                "--expr",
                "with import ./. {}; "
                f"if ({attr} ? strictDeps) then {attr}.strictDeps else false",
            ]
        )
        .decode()
        .strip()
    )

    if strict_deps_status == "true":
        return True

    return False


def get_outputs(attr: str, nixgits: Path) -> tuple[dict[str, str], dict[str, str]]:
    """get json from nix build and convert it class objects"""
    nixpkgs = Path(f"{nixgits}/nixpkgs")
    strict_nixpkgs = Path(f"{nixgits}/my-nixpkgs")

    os.environ["diffNixpkgs"] = str(nixpkgs)
    os.environ["diffStrictNixpkgs"] = str(strict_nixpkgs)
    os.environ["diffAttr"] = attr

    strict_expr = Path("@strictexpr@")
    expr = Path("@expr@")

    # os.chdir(strict_nixpkgs)
    output_strict = subprocess.check_output(
        [
            "nix",
            "build",
            "--json",
            "--impure",
            "-f",
            strict_expr,
            # "--expr",
            # "with import ./. {}; "
            # f"{attr}.overrideAttrs (oldAttrs: "
            # "{ strictDeps = true; meta = oldAttrs.meta // "
            # "lib.optionalAttrs (oldAttrs ? outputs )  { outputsToInstall = oldAttrs.outputs; }; })",
        ]
    )

    # os.chdir(nixpkgs)
    output = subprocess.check_output(
        [
            "nix",
            "build",
            "--json",
            "--impure",
            "-f",
            expr,
            # "--expr",
            # "with import ./. {}; "
            # f"{attr}.overrideAttrs (oldAttrs: "
            # "{ meta = oldAttrs.meta // "
            # "lib.optionalAttrs (oldAttrs ? outputs ) { outputsToInstall = oldAttrs.outputs; }; })",
        ]
    )

    output_strict_dict: dict[str, str] = json.loads(output_strict.strip())[0]["outputs"]
    output_dict: dict[str, str] = json.loads(output.strip())[0]["outputs"]

    return output_dict, output_strict_dict


def main() -> None:
    """main"""
    nixgits = os.getenv("NIXGITS") or f"{os.getenv('HOME')}/nixgits"
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            usage:
                diffing ".#bash"
                diffing --file filecontainingattrs
            """
        ),
    )
    parser.add_argument("attrs", nargs="*")
    parser.add_argument("--file", help="a file containing attrs")
    parser.add_argument(
        "--force",
        help="diff even if strictDeps is already enabled",
        action="store_true",
    )
    args = parser.parse_args()
    attrs: list[str] = []
    if args.file:
        attrs = Path(args.file).read_text(encoding="UTF-8").splitlines()
    else:
        attrs = [a.replace(".#", "") for a in args.attrs]

    print(f"{attrs}\n")
    for attr in attrs:
        if not args.force:
            if is_strict_already(attr, Path(nixgits)):
                txt = f"{attr} has strictDeps enabled already!".center(100, "-")
                print(txt)
                print()
                continue

        outputs, outputs_strict = get_outputs(attr, Path(nixgits))

        for output_name, output_path in outputs.items():
            outputs_strict_path = outputs_strict[output_name]
            txt = f"diffing output {output_name} of {attr}".center(100, "-")
            print(txt)
            print(f"normal: {output_path}")
            print(f"strict: {outputs_strict_path}")
            print()

            subprocess.run(
                ["diffoscope", output_path, outputs_strict_path], check=False
            )


if __name__ == "__main__":
    main()
