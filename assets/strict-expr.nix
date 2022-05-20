let
  pkgs = import (builtins.getEnv "diffStrictNixpkgs") { };
  lib = pkgs.lib;
  attr = builtins.getEnv "diffAttr";
in
pkgs.${attr}.overrideAttrs (oldAttrs: {
  strictDeps = true;
} // lib.optionalAttrs (oldAttrs ? meta)
  {
    meta = oldAttrs.meta // lib.optionalAttrs (oldAttrs ? outputs)
      { outputsToInstall = oldAttrs.outputs; };
  })
