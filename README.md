# diffing
find strictDeps problems


specify the NIXPKGS env var



example of making a attrlist file

```
cat ./pkgs/top-level/all-packages.nix | rg "shells" | sort -hk1 | cut -f1 -d '=' | sed 's/  //' > attrlist
```
