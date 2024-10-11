{
  description = "Docsy helps you to manage your documentation in a better way.";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.poetry2nix.url = "github:nix-community/poetry2nix";

  outputs = { self, nixpkgs, poetry2nix }:
    let
      system = "x86_64-darwin";
      pkgs = nixpkgs.legacyPackages.${system};
      # create a custom "mkPoetryApplication" API function that under the hood uses
      # the packages and versions (python3, poetry etc.) from our pinned nixpkgs above:
      inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; })
        mkPoetryApplication;
      myPythonApp = mkPoetryApplication { projectDir = ./.; };
    in {
      apps.${system} = {
        # nix run .#docsy_dashboard 
        docsy_dashboard = {
          type = "app";
          program = "${myPythonApp}/bin/docsy_dashboard";
        };
        docsy_slack = {
          type = "app";
          program = "${myPythonApp}/bin/docsy_slack";
        };
      };
      devShells.x86_64-darwin.default = pkgs.mkShell { buildInputs = [ pkgs.python3 pkgs.poetry ]; };
    };
}
