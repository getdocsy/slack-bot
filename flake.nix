{
  description = "Python application packaged using poetry2nix";

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
      apps.${system}.default = {
        type = "app";
        program = "${myPythonApp}/bin/docsy_dashboard";
      };
    };
}
