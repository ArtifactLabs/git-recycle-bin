{ pkgs ? (import (builtins.fetchTarball {
  url = "https://github.com/nixos/nixpkgs/tarball/23.11";
  sha256 = "1ndiv385w1qyb3b18vw13991fzb9wg4cl21wglk89grsfsnra41k";
}) { }) }:

(import ./mkPythonShell.nix) {
  inherit pkgs;
  pythonVersion = "3.8";
}

