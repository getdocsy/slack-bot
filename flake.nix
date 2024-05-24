{
  description = "Docsy App";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix, ... }:
    flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs { inherit system; };
      inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
    in {
        devShell = pkgs.mkShell {
          name = "docsy dev shell";
          nativeBuildInputs = [
            pkgs.python3 pkgs.poetry
          ];
          shellHook = ''
            source .env
          '';
        };

        packages.app = mkPoetryApplication {
          projectDir = ./.;
        };

        packages.default = mkPoetryApplication {
          projectDir = ./.;
        };
    });
}
