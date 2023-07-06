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
    strict_nixpkgs = Path.cwd()
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


def get_outputs_strict(pr: int, attr: str) -> bytes:
    strict_expr = Path("@strictexpr@")

    if pr != 0:
        output_strict_1 = subprocess.run(
            [
                "nixpkgs-review",
                "pr",
                str(pr),
                "-p",
                attr,
                "--run",
                f"echo -n 'STOREPATH=' && readlink -f ./results/{attr}",
            ],
            check=True,
            stdout=subprocess.PIPE,
        )
        output_strict_2 = subprocess.run(
            ["grep", "^STOREPATH"],
            check=True,
            input=output_strict_1.stdout,
            stdout=subprocess.PIPE,
        )
        output_strict_3 = subprocess.run(
            ["sed", "s/STOREPATH=//"],
            check=True,
            input=output_strict_2.stdout,
            stdout=subprocess.PIPE,
        )
        output_strict_4 = subprocess.run(
            ["nix", "derivation", "show", "--stdin"],
            check=True,
            input=output_strict_3.stdout,
            stdout=subprocess.PIPE,
        )
        # for converting 'nix derivation show' output to 'nix build --json' compatible output
        # derivation show '.[] | .outputs'
        # { "out": { "path": "/nix/store/..."} }
        # nix build '.[] | .outputs'
        # { "out": "/nix/store/..." }
        output_strict = subprocess.check_output(
            ["jq", ".[] | .outputs | [{ outputs: map_values(.path)}]"],
            input=output_strict_4.stdout,
        )
    else:
        output_strict = subprocess.check_output(
            [
                "nix",
                "build",
                "--json",
                "--impure",
                "-f",
                strict_expr,
            ]
        )

    return output_strict


def get_outputs(
    attr: str, nixgits: Path, pr: int
) -> tuple[dict[str, str], dict[str, str]]:
    """get json from nix build and convert it class objects"""
    nixpkgs = Path(f"{nixgits}/nixpkgs")
    strict_nixpkgs = Path.cwd()

    os.environ["diffNixpkgs"] = str(nixpkgs)
    os.environ["diffStrictNixpkgs"] = str(strict_nixpkgs)
    os.environ["diffAttr"] = attr

    expr = Path("@expr@")

    output_strict = get_outputs_strict(pr, attr)

    output = subprocess.check_output(
        [
            "nix",
            "build",
            "--json",
            "--impure",
            "-f",
            expr,
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
    parser.add_argument("--pr", help="pr to check, diffed as the strict nixpkgs")
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

    p_r = args.pr or 0

    print(f"{attrs}\n")
    for attr in attrs:
        # when pr is specified there should be no checking
        if p_r == 0 and not args.force:
            if is_strict_already(attr, Path(nixgits)):
                txt = f"{attr} has strictDeps enabled already!".center(100, "-")
                print(txt)
                print()
                continue

        outputs, outputs_strict = get_outputs(attr, Path(nixgits), p_r)

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
