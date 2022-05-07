# diffing
find strictDeps problems


point the NIXGITS env var to a directory containing nixpkgs and my-nixpkgs

my-nixpkgs will be the one you commit strictDeps fixes to


## usage
```bash
nix run "github:Artturin/diffing" ".#bash"
```

example of making a attrlist file

```
cat ./pkgs/top-level/all-packages.nix | rg "shells" | sort -hk1 | cut -f1 -d '=' | sed 's/  //' > attrlist
```
