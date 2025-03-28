{ pkgs ? (import (builtins.fetchTarball {
  url = "https://github.com/nixos/nixpkgs/tarball/24.05";
  sha256 = "1lr1h35prqkd1mkmzriwlpvxcb34kmhc9dnr48gkm8hh089hifmx";
}) {}) }:

let
  git-recycle-bin = import ./default.nix { inherit pkgs; };
in pkgs.mkShellNoCC {
  name = "git-recycle-bin test+lint+docs env";

  packages = [
    git-recycle-bin

    pkgs.nix # for checking across many python versions
    pkgs.just
    pkgs.ripgrep

    pkgs.shellcheck
    pkgs.nodePackages.markdownlint-cli
    pkgs.plantuml

    # Python development tools for VS Code integration
    pkgs.python311
    pkgs.python311Packages.black
    pkgs.python311Packages.isort
    pkgs.python311Packages.python-lsp-server  # Language server for better VS Code support

    # Type checking and linting tools
    pkgs.python311Packages.pylint
    pkgs.python311Packages.mypy
    pkgs.python311Packages.types-colorama
    pkgs.python311Packages.types-python-dateutil

    # Sphinx documentation tools
    pkgs.python311Packages.sphinx
    pkgs.python311Packages.pydata-sphinx-theme
    pkgs.python311Packages.sphinx-design  # Sphinx extension for design elements and components
    pkgs.python311Packages.sphinxcontrib-plantuml  # PlantUML extension for Sphinx

    # RST linting tools
    pkgs.python311Packages.rstcheck
    pkgs.python311Packages.restructuredtext-lint
  ];

  shellHook = ''
    export JUST_UNSTABLE=1

    # Set up Python path for development
    export PYTHONPATH="$PWD/src:$PYTHONPATH"
  '';
}
