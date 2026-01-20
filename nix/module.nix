flake:
{
  config,
  lib,
  pkgs,
  ...
}:

let
  cfg = config.services.internet-archive;
  inherit (lib)
    mkEnableOption
    mkOption
    types
    mkIf
    ;
in
{
  options.services.internet-archive = {
    enable = mkEnableOption "Internet Archive Save Page Now service";

    url = mkOption {
      type = types.str;
      description = "URL to archive";
      example = "https://example.com/";
    };

    schedule = mkOption {
      type = types.str;
      default = "weekly";
      description = "Systemd calendar expression for when to run the archiver";
      example = "daily";
    };

    debug = mkOption {
      type = types.bool;
      default = false;
      description = "Enable debug output";
    };

    environmentFile = mkOption {
      type = types.nullOr types.path;
      default = null;
      description = ''
        Path to an environment file containing:
        - INTERNET_ARCHIVE_SPN2_URL
        - INTERNET_ARCHIVE_ACCESS_KEY
        - INTERNET_ARCHIVE_PRIVATE_KEY
        - INTERNET_ARCHIVE_STATUS_CHECK_URL
      '';
      example = "/run/secrets/internet-archive.env";
    };
  };

  config = mkIf cfg.enable {
    assertions = [
      {
        assertion = cfg.environmentFile != null;
        message = "services.internet-archive.environmentFile must be set";
      }
    ];

    systemd.services.internet-archive = {
      description = "Archive URL to Internet Archive";
      after = [ "network-online.target" ];
      wants = [ "network-online.target" ];

      serviceConfig = {
        Type = "oneshot";
        EnvironmentFile = cfg.environmentFile;
        ExecStart =
          let
            pkg = flake.packages.${pkgs.system}.default;
            debugFlag = if cfg.debug then "--debug" else "";
          in
          "${pkg}/bin/python ${flake}/main.py ${lib.escapeShellArg cfg.url} ${debugFlag}";

        # Hardening
        DynamicUser = true;
        NoNewPrivileges = true;
        ProtectSystem = "strict";
        ProtectHome = true;
        PrivateTmp = true;
      };
    };

    systemd.timers.internet-archive = {
      description = "Timer for Internet Archive service";
      wantedBy = [ "timers.target" ];

      timerConfig = {
        OnCalendar = cfg.schedule;
        Persistent = true;
        RandomizedDelaySec = "5min";
      };
    };
  };
}
