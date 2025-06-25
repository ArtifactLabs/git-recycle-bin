{ pkgs ? (import (builtins.fetchTarball {
  url = "https://github.com/nixos/nixpkgs/tarball/25.05";
  sha256 = "1lr1h35prqkd1mkmzriwlpvxcb34kmhc9dnr48gkm8hh089hifmx";
}) { }) }:

(import ./mkGitShell.nix) {
  inherit pkgs;
  gitVersion = "2.49.0";
  nixpkgsRevision = "1c1c9b3f5ec0421eaa0f22746295466ee6a8d48f";
} 