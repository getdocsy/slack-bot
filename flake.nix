{
  description = "Docsy App";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = import nixpkgs { inherit system; };
      in {
        devShell = pkgs.mkShell {
          name = "docsy dev shell";
          nativeBuildInputs = [
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
        };

        packages.app = pkgs.buildPythonApplication {
          pname = "docsy";
          version = "1.0";
          src = ./.;
        };

        packages.default = pkgs.python3Packages.buildPythonApplication {
          pname = "docsy";
          version = "1.0";
          src = ./.;
        };
    });
}
