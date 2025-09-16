{
  buildPythonPackage,
  setuptools,
  pytest,
  pytest-cov,
  git,
  maya,
  colorama,
  dateparser
}:
let
  pyproject = builtins.fromTOML (builtins.readFile ./pyproject.toml);
  project = pyproject.project;
in
buildPythonPackage rec {
  pname = project.name;
  inherit (project) version;

  src = ./.;

  format = "pyproject";

  nativeCheckInputs = [
    setuptools

    pytest
    pytest-cov

    git
  ];

  propagatedBuildInputs = [
    git
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
