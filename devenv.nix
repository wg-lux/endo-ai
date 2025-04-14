{ pkgs, lib, config, inputs, ... }:

let
  # --- Project Configuration ---
  DJANGO_MODULE = "endo_ai";
  host = "localhost";
  port = "8183";

  # --- Directory Structure ---
  dataDir = "data";
  importDir = "${dataDir}/import";
  importVideoDir = "${importDir}/video";
  importReportDir = "${importDir}/report";
  importLegacyAnnotationDir = "${importDir}/legacy_annotations";
  exportDir = "${dataDir}/export";
  exportFramesRootDir = "${exportDir}/frames";
  exportFramesSampleExportDir = "${exportFramesRootDir}/test_outputs";
  modelDir = "${dataDir}/models";
  confDir = "./conf"; # Define confDir here

  # --- Nix Packages & Build Inputs ---
  python = pkgs.python311Full;
  buildInputs = with pkgs; [
    python
    stdenv.cc.cc
    # cudaPackages.cuda_cudart # Uncomment if needed
    # cudaPackages.cudnn      # Uncomment if needed
  ];
  runtimePackages = with pkgs; [
    cudaPackages.cuda_nvcc # Needed for runtime? Check dependencies
    stdenv.cc.cc
    ffmpeg-headless.bin
    tesseract
    zsh # If you prefer zsh as the shell
  ];

  # --- Helper Functions ---
  uv = "${pkgs.uv}/bin/uv"; # Shortcut for uv command

in
{
  # --- Basic devenv Settings ---
  # shell = pkgs.zsh; # Uncomment to force zsh
  dotenv.enable = true; # Automatically load .env file

  # --- Nix Packages ---
  packages = runtimePackages;

  # --- Environment Variables (Set by Nix) ---
  # Variables needed during build or directly by tools run within Nix shell
  env = {
    LD_LIBRARY_PATH = lib.makeLibraryPath buildInputs + ":/run/opengl-driver/lib:/run/opengl-driver-32/lib";
    CONF_DIR = confDir; # Pass confDir defined above
  };

  # --- Language Support ---
  languages.python = {
    enable = true;
    package = python; # Use the defined python version
    uv.enable = true; # Use uv for environment management
  };

  # --- Scripts (Reusable shell snippets) ---
  scripts = {
    # Script to export non-secret Nix variables for env_setup.py
    export-nix-vars.exec = ''
      cat > .devenv-vars.json << EOF
      {
        "DJANGO_MODULE": "${DJANGO_MODULE}",
        "HOST": "${host}",
        "PORT": "${port}",
        "CONF_DIR": "${confDir}",
        "HOME_DIR": "$HOME",
        "WORKING_DIR": "$PWD"
      }
      EOF
      echo "Exported Nix variables to .devenv-vars.json"
    '';

    # Script to ensure necessary directories exist
    ensure-dirs.exec = ''
      mkdir -p ${dataDir} ${importDir} ${importVideoDir} ${importReportDir} \
                 ${exportDir} ${modelDir} ${importLegacyAnnotationDir} \
                 ${exportFramesRootDir} ${confDir}
      chmod -R 700 ${dataDir} # Adjust permissions as needed
    '';

    # Scripts to switch Django settings
    set-prod-settings.exec = "${uv} run python scripts/set_production_settings.py";
    set-dev-settings.exec = "${uv} run python scripts/set_development_settings.py";

    # Development server script
    run-dev-server.exec = ''
      echo "Running dev server on ${host}:${port}"
      ${uv} run python manage.py runserver ${host}:${port}
    '';

    # Production server script (using Daphne)
    run-prod-server.exec = ''
      echo "Running production server on port ${port}"
      ${uv} run daphne ${DJANGO_MODULE}.asgi:application -p ${port}
    '';

    # Other utility scripts
    transcode-videos-in-dir.exec = "./scripts/transcode_videos.sh";
    demo-summary.exec = "${uv} run python scripts/summary_after_demo_pipe.py";
    demo-pipe.exec = ''
      ./scripts/demo_pipe.sh
      demo-summary
    '';
  };

  # --- Tasks (Runnable commands via `devenv task run <name>`) ---
  tasks = {
    # Environment Setup
    "env:build" = {
      description = "Generate/update .env file with secrets and config";
      exec = "export-nix-vars && ${uv} run env_setup.py";
    };

    # Directory Setup
    "setup:dirs" = {
      description = "Ensure all necessary data directories exist";
      exec = "ensure-dirs";
    };

    # Database Setup
    "db:makemigrations" = {
      description = "Create Django database migrations";
      exec = "${uv} run python manage.py makemigrations";
    };
    "db:migrate" = {
      description = "Apply Django database migrations";
      exec = "${uv} run python manage.py migrate";
    };
    "db:load-base-data" = {
      description = "Load initial base data into the database";
      exec = "${uv} run python manage.py load_base_db_data";
    };
    "db:init" = {
      description = "Run initial database setup (migrations, base data)";
      after = [ "db:makemigrations" "db:migrate" "db:load-base-data" ];
    };

    # Configuration Setup
    "conf:init" = {
      description = "Initialize configuration files";
      exec = "${uv} run python scripts/make_conf.py";
    };

    

    # Static Files
    "static:collect" = {
      description = "Collect Django static files";
      exec = "${uv} run python manage.py collectstatic --noinput";
    };

    # Full Initialization Task
    "deploy:init" = {
      description = "Perform initial project setup (dirs, conf, env, db)";
      after = [ "setup:dirs" "conf:init" "env:build" "db:init" ];
      exec = "echo 'Initial setup complete. Dependencies installed via uv sync.'";
    };
    # Full Initialization Task
    "deploy:init-dev" = {
      description = "Perform initial project setup (dirs, conf, env, db)";
      after = [ "setup:dirs" "conf:init" "env:build" "db:init" ];
      exec = "echo 'Initial setup complete. Dependencies installed via uv sync.'";
    };
  };

  # --- Processes (Long-running services via `devenv process up <name>`) ---
  processes = {
    django-dev.exec = "run-dev-server"; # Use dev server script
  };

  # --- Shell Entry Hook ---
  enterShell = ''
    # Activate Python virtual environment managed by uv
    if [ -f ".devenv/state/venv/bin/activate" ]; then
      source .devenv/state/venv/bin/activate
    else
      echo "Warning: uv virtual environment activation script not found."
    fi

    # Check if .env exists and is not empty, run env:build if needed
    if [ ! -s .env ]; then
      echo "Notice: .env file is missing or empty. Running 'devenv task run env:build'..."
      ${config.tasks."env:build".exec}
    fi

    echo "Development environment ready."
  '';
}
