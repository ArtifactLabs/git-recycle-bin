{ pkgs ? (import (builtins.fetchTarball {
    url = "https://github.com/nixos/nixpkgs/tarball/24.05";
    sha256 = "1lr1h35prqkd1mkmzriwlpvxcb34kmhc9dnr48gkm8hh089hifmx";
  }) {} )
, pythonVersion ? "python311"
}:

let
  pythonPackages = pkgs.${pythonVersion + "Packages"};
in
pythonPackages.buildPythonApplication rec {
  pname = "git-recycle-bin";
  version = "0.2.6";

  src = pkgs.lib.fileset.toSource {
    root = ./.;
    fileset = pkgs.lib.fileset.unions [
      # Python source files - filter out  __pycache__ and linter cruft
      (pkgs.lib.fileset.fileFilter (file: file.hasExt "py") ./src)

      # Setup and configuration files
      ./setup.py
      ./pyproject.toml

      # Test files for checkPhase
      (pkgs.lib.fileset.fileFilter (file: file.hasExt "py") ./tests)

      # Auxiliary scripts needed for postInstall
      ./aux/git_add_ssh_remote.sh

      # License and readme files
      ./LICENSE
      ./readme.md
    ];
  };
  format = "setuptools";

  propagatedBuildInputs = [ pkgs.git ] ++ pythonPath;

  pythonPath = with pythonPackages; [
    maya
    colorama
    dateparser
    pytest
    pytest-cov
  ];

  checkInputs = with pythonPackages; [ pytest pytest-cov ];

  checkPhase = ''
    runHook preCheck
    export PYTHONPATH="$PYTHONPATH:$PWD:$PWD/src"
    python -m pytest -vv
    runHook postCheck
  '';

  postInstall = ''
    install -Dm755 ${./aux/git_add_ssh_remote.sh} $out/bin/git_add_ssh_remote.sh
  '';
}
