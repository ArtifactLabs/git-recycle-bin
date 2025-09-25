{ pkgs ? (import (builtins.fetchTarball {
  url = "https://github.com/nixos/nixpkgs/tarball/25.05";
  sha256 = "1lr1h35prqkd1mkmzriwlpvxcb34kmhc9dnr48gkm8hh089hifmx";
}) { }) }:

(import ./mkGitShell.nix) {
  inherit pkgs;
  gitVersion = "2.38.0";
  nixpkgsRevision = "a634c8f6c1fbf9b9730e01764999666f3436f10a";
} 