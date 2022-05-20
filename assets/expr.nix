let
  pkgs = import (builtins.getEnv "diffNixpkgs") { };
  lib = pkgs.lib;
  attr = builtins.getEnv "diffAttr";
in
pkgs.${attr}.overrideAttrs (oldAttrs: { } // lib.optionalAttrs (oldAttrs ? meta)
  {
    meta = oldAttrs.meta // lib.optionalAttrs (oldAttrs ? outputs)
      { outputsToInstall = oldAttrs.outputs; };
  })
