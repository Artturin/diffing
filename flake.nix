{
  inputs = {
    lib-aggregate = {
      url = "github:nix-community/lib-aggregate";
    };
    nixpkgs = {
      url = "github:NixOS/nixpkgs/nixos-unstable";
    };
  };

  outputs =
    inputs:
    let
      inherit (inputs.lib-aggregate) lib;
      diffingLambda =
        pkgs:
        pkgs.substituteAll {
          name = "diffing";
          src = ./diffing.py;
          dir = "bin";
          isExecutable = true;
          strictexpr = ./assets/strict-expr.nix;
          expr = ./assets/expr.nix;
          # Minimal diffoscope should be enough.
          diffoscope = lib.getExe pkgs.diffoscopeMinimal;
          postInstall = ''
            sed -i '1 i#!${pkgs.python3.interpreter}' $out/bin/diffing
          '';
        };
    in
    lib.flake-utils.eachDefaultSystem (
      system:
      let
        pkgs = inputs.nixpkgs.legacyPackages.${system};
      in
      {
        packages.default = diffingLambda pkgs;
      }
    )
    // {

      overlays.default = (
        _: prev: {
          diffing = diffingLambda prev;
        }
      );
    };
}
