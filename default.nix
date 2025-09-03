{ pkgs ? (import (builtins.fetchTarball {
    url = "https://github.com/nixos/nixpkgs/tarball/24.05";
    sha256 = "1lr1h35prqkd1mkmzriwlpvxcb34kmhc9dnr48gkm8hh089hifmx";
  }) {} ) }:

let
  pyproject = builtins.fromTOML (builtins.readFile ./pyproject.toml);
  project = pyproject.project;
in
pkgs.python311Packages.buildPythonPackage rec {
  pname = project.name;
  inherit (project) version;

  src = ./.;

  format = "pyproject";

  nativeCheckInputs = with pkgs.python311Packages; [
    setuptools

    pytest
    pytest-cov

    pkgs.git
  ];

  propagatedBuildInputs = with pkgs.python311Packages; [
    pkgs.git
    maya
    colorama
    dateparser
  ];

  checkPhase = ''
     runHook preCheck
     pytest
     runHook postCheck
  '';

  postInstall = ''
    install -Dm755 ${./aux/git_add_ssh_remote.sh} $out/bin/git_add_ssh_remote.sh
  '';
}
