# diffing
find strictDeps problems


point the NIXGITS env var to a directory containing 2 nixpkgs directories called nixpkgs and my-nixpkgs

`diffing ".#bash"`
will build bash in both repositories and then diff their outputs
this is to allow you to make changes in `my-nixpkgs` and then run diffing again


## usage
```bash
nix run "github:Artturin/diffing" ".#bash"
```

example of making a attrlist file

```
cat ./pkgs/top-level/all-packages.nix | rg "shells" | sort -hk1 | cut -f1 -d '=' | sed 's/  //' > attrlist
```
