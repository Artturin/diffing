{
  inputs = {
    lib-aggregate = {url = "github:nix-community/lib-aggregate";};
    nixpkgs = {url = "github:NixOS/nixpkgs/nixos-unstable";};
  };

  outputs = inputs: let
    inherit (inputs.lib-aggregate) lib;
  in
    lib.flake-utils.eachDefaultSystem (system: let
      pkgs = inputs.nixpkgs.legacyPackages.${system};
    in {
      packages.default =
        pkgs.writers.writePython3Bin "diffing" {flakeIgnore = ["E501"];}
        (builtins.readFile ./diffing.py);
    });
}
