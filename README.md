# diffing
find strictDeps problems


point the NIXGITS env var to a directory containing a nixpkgs dir

That repo will be compared to the current dir you're in so make sure both are at the same rev

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


### mass enabling strictDeps in a dependency tree

first i run

```
nix-diff $(nix eval --raw ".#bash.drvPath") $(nix eval --raw --expr 'with import ./. { config = { strictDepsByDefault = true; }; }; bash.drvPath' --impure)
```

then i pick derivations which don't already have strictDeps, for example

```diff
• The input derivation named `libffi-3.4.2` differs
  - /nix/store/0m0ijn5d1nh5mfxg5y687br7ywvqlw3b-libffi-3.4.2.drv:{dev,out}
  + /nix/store/pdab3mkc93a6llj9x3xakrx5bfv0nkm1-libffi-3.4.2.drv:{dev,out}
  • The environments do not match:
      strictDeps=1
```

then i put the attr in a `attrlist` file and run

```
diffing --file attrlist
```

and read through the whole diff and if it looks fine i enable strictDeps
