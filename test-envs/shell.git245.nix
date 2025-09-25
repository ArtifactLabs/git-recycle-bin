{ pkgs ? (import (builtins.fetchTarball {
  url = "https://github.com/nixos/nixpkgs/tarball/25.05";
  sha256 = "1lr1h35prqkd1mkmzriwlpvxcb34kmhc9dnr48gkm8hh089hifmx";
}) { }) }:

(import ./mkGitShell.nix) {
  inherit pkgs;
  gitVersion = "2.45.2";
  nixpkgsRevision = "d9f258945d3532e399d7f73fcd9b6fa5b4393e01";
} 