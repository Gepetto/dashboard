{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = with pkgs; [
    cyrus_sasl
    gettext
    openldap
    python3
    postgresql
    (poetry.withPlugins(ps: with ps; [poetry-plugin-up]))
  ];
  shellHook = "source .venv/bin/activate";
}
