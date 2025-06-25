# This gives a shell in which we can test commands across different git versions.
# It is parameterized by the git version and uses specific nixpkgs revisions.
{ pkgs, gitVersion, nixpkgsRevision }:

let
  # Import specific nixpkgs revision for the git version
  gitPkgs = import (builtins.fetchTarball {
    url = "https://github.com/nixos/nixpkgs/tarball/${nixpkgsRevision}";
  }) { };
  
  gitPkg = gitPkgs.git;

in pkgs.mkShellNoCC {
  name = "git-recycle-bin-git-${gitVersion}";

  packages = [ gitPkg pkgs.python311 pkgs.python311Packages.pytest ];

  shellHook = ''
    export PYTHONPATH="$PWD:$PWD/src:$PYTHONPATH"
    echo "Git version: $(git --version)"
  '';
} 