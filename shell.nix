{ pkgs ? (import (builtins.fetchTarball {
  url = "https://github.com/nixos/nixpkgs/tarball/22.11";
  sha256 = "11w3wn2yjhaa5pv20gbfbirvjq6i3m7pqrq2msf0g7cv44vijwgw";
}) {}) }:
pkgs.mkShell {
  name = "git-recycle-bin";
  packages = (import ./deps.nix) { inherit pkgs; };
}
