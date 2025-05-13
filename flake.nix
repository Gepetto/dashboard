{
  description = "LAAS intranet";

  inputs = {
    flake-parts.url = "github:hercules-ci/flake-parts";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [ "x86_64-linux" "aarch64-darwin" ];
      perSystem = { pkgs, ... }: {
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.gettext
            pkgs.openldap
            pkgs.cyrus_sasl
            (pkgs.poetry.withPlugins (p: [ p.poetry-plugin-up ]))
            pkgs.postgresql
          ];
        };
      };
    };
}
