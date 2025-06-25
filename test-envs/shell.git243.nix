{ pkgs ? (import (builtins.fetchTarball {
  url = "https://github.com/nixos/nixpkgs/tarball/25.05";
  sha256 = "1lr1h35prqkd1mkmzriwlpvxcb34kmhc9dnr48gkm8hh089hifmx";
}) { }) }:

(import ./mkGitShell.nix) {
  inherit pkgs;
  gitVersion = "2.43.0";
  nixpkgsRevision = "007604529b133db7ef40e687cd95d88c37e5fe8a";
} 