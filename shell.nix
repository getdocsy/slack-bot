# shell.nix
let
  # We pin to a specific nixpkgs commit for reproducibility.
  # I use a pretty old one (last 23.05 because newer had problems with python-pkgs.slack-bolt (https://stackoverflow.com/questions/77903321/importerror-cannot-import-name-mock-s3-from-moto)
  # Check for new commits at https://status.nixos.org.
  pkgs = import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/3eaeaeb6b1e08a016380c279f8846e0bd8808916.tar.gz") {};
in pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (python-pkgs: [
      python-pkgs.slack-bolt
      python-pkgs.openai
      python-pkgs.gitpython
      python-pkgs.pygithub
    ]))
  ];
  shellHook = ''
    source .env
  '';
}
