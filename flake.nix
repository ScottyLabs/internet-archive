{
  description = "Archives a page of your choice to the Internet Archive";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      pyproject-nix,
      uv2nix,
      pyproject-build-systems,
    }:
    let
      # System-independent outputs
      nixosModule = import ./nix/module.nix self;
    in
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        lib = pkgs.lib;

        # Load the workspace from uv.lock
        workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

        # Create base Python set with pyproject.nix builders
        pythonBase = pkgs.callPackage pyproject-nix.build.packages {
          python = pkgs.python314;
        };

        # Generate overlay from uv.lock
        overlay = workspace.mkPyprojectOverlay {
          sourcePreference = "wheel";
        };

        # Compose all overlays into final package set
        pythonSet = pythonBase.overrideScope (
          lib.composeManyExtensions [
            pyproject-build-systems.overlays.default
            overlay
          ]
        );

        # Build virtual environment for deployment
        venv = pythonSet.mkVirtualEnv "internet-archive-env" workspace.deps.default;
      in
      {
        packages = {
          default = venv;
          internet-archive = venv;
        };

        apps.default = {
          type = "app";
          program = "${venv}/bin/python";
        };

        devShells.default = pkgs.mkShell {
          packages = [
            venv
            pkgs.uv
          ];

          env = {
            UV_NO_SYNC = "1";
            UV_PYTHON_DOWNLOADS = "never";
          };

          shellHook = ''
            unset PYTHONPATH
          '';
        };

        formatter = pkgs.nixfmt;
      }
    )
    // {
      nixosModules.default = nixosModule;
      nixosModules.internet-archive = nixosModule;
    };
}
