# This gives a shell in which we can test pip install and pytest across all supported python versions.
# It is parameterized by the python version and nixpkgs, as not all nixpkgs has all python versions.
{ pkgs, pythonVersion }:

let
  pythonVersionNoDot = builtins.replaceStrings [ "." ] [ "" ] pythonVersion;
  pythonPkg = pkgs.${"python" + pythonVersionNoDot};

  # Override Python to ensure it has proper OpenSSL support for hash algorithms
  python = pythonPkg.override {
    openssl = pkgs.openssl;
    enableOptimizations =
      false; # Disable optimizations that might break hash algorithms
  };

  pythonPackages = python.pkgs;
in pkgs.mkShellNoCC {
  name = "git-recycle-bin-py${pythonVersionNoDot}";

  packages = [ python pythonPackages.pytest pkgs.openssl ];

  shellHook = ''
    python -m venv .venv${pythonVersionNoDot}
    source .venv${pythonVersionNoDot}/bin/activate
    export PYTHONPATH="$PWD:$PWD/src:$PWD/.venv${pythonVersionNoDot}/lib/python${pythonVersion}/site-packages:$PYTHONPATH"
    pip install .
  '';
}
