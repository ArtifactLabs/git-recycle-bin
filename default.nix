{ pkgs ? (import (builtins.fetchTarball {
    url = "https://github.com/nixos/nixpkgs/tarball/24.05";
    sha256 = "1lr1h35prqkd1mkmzriwlpvxcb34kmhc9dnr48gkm8hh089hifmx";
  }) {} ) }:

pkgs.python311Packages.buildPythonApplication rec {
  pname = "git-recycle-bin";
  version = "0.2.5";

  src = ./.;
  format = "setuptools";

  propagatedBuildInputs = [ pkgs.git ] ++ pythonPath;

  pythonPath = with pkgs.python311Packages; [
    maya
    colorama
    dateparser
    pytest
  ];

  postInstall = ''
    install -Dm755 ${./aux/git_add_ssh_remote.sh} $out/bin/git_add_ssh_remote.sh
  '';
}
