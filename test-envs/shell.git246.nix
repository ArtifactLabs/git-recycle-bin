{ pkgs ? (import (builtins.fetchTarball {
  url = "https://github.com/nixos/nixpkgs/tarball/25.05";
  sha256 = "1lr1h35prqkd1mkmzriwlpvxcb34kmhc9dnr48gkm8hh089hifmx";
}) { }) }:

(import ./mkGitShell.nix) {
  inherit pkgs;
  gitVersion = "2.46.0";
  nixpkgsRevision = "2c36ece932b8c0040893990da00034e46c33e3e7";
} 