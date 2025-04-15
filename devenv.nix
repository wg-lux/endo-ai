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
    "env:clean" = {
      description = "Remove the uv virtual environment and lock file for a clean sync";
      exec = ''
        echo "Removing uv virtual environment: .devenv/state/venv"
        rm -rf .devenv/state/venv
        echo "Removing uv lock file: uv.lock"
        rm -f uv.lock
        echo "Environment cleaned. Re-enter the shell (e.g., 'exit' then 'devenv up') to trigger uv sync."
      '';
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
    "db:merge-migrations" = {
      description = "Merge conflicting Django database migrations";
      exec = "${uv} run python manage.py makemigrations --merge";
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
    # Define commands as shell variables using the 'uv' helper variable
    export SYNC_CMD="${uv} sync" # Use the 'uv' variable defined in the let block

    # Ensure dependencies are synced using uv
    # Check if venv exists. If not, run sync verbosely. If it exists, sync quietly.
    if [ ! -d ".devenv/state/venv" ]; then
       echo "Virtual environment not found. Running initial uv sync..."
       $SYNC_CMD || echo "Error: Initial uv sync failed. Please check network and pyproject.toml."
    else
       # Sync quietly if venv exists
       echo "Syncing Python dependencies with uv..."
       $SYNC_CMD --quiet || echo "Warning: uv sync failed. Environment might be outdated."
    fi

    # Activate Python virtual environment managed by uv
    ACTIVATED=false
    if [ -f ".devenv/state/venv/bin/activate" ]; then
      source .devenv/state/venv/bin/activate
      ACTIVATED=true
      echo "Virtual environment activated."
    else
      echo "Warning: uv virtual environment activation script not found. Run 'devenv task run env:clean' and re-enter shell."
    fi

    # Check if .env exists and is not empty, run env:build if needed
    if [ ! -s .env ]; then
      echo "Notice: .env file is missing or empty. Running 'devenv task run env:build'..."
      # Use the Nix path to uv directly as venv might not be active yet if sync failed
      ${config.tasks."env:build".exec}
    fi

    echo "Development environment ready."

    # Add checks only if venv was activated
    if [ "$ACTIVATED" = true ]; then
      echo "--- Environment Checks ---"
      # Check endoreg-db installation location
      echo "Checking endoreg-db installation:"
      ${uv} pip show endoreg-db | grep Location || echo "  endoreg-db not found or 'uv pip show' failed."

      # Check lx-anonymizer installation location (more reliably via list --editable)
      echo "Checking lx-anonymizer installation (editable):"
      if ${uv} pip list --editable | grep -q lx-anonymizer; then
          echo "  lx-anonymizer found in editable installs."
          # Optionally, still try pip show for location info, but treat failure as less critical
          ${uv} pip show lx-anonymizer | grep Location || echo "  'uv pip show lx-anonymizer' could not retrieve location details (expected if not on PyPI)."
      else
          echo "  lx-anonymizer NOT found in editable installs. Check 'uv sync' output and 'pyproject.toml' [tool.uv.sources]."
          echo "  Ensure the directory './lx-anonymizer' exists and contains a valid package."
      fi

      # Check if local packages are installed in editable mode
      echo "Checking editable installs:"
      # Check endo-ai, endoreg-db, and lx-anonymizer
      ${uv} pip list --editable | grep -E 'endo-ai|endoreg-db|lx-anonymizer' || echo "  Local packages (endo-ai, endoreg-db, lx-anonymizer) not found in editable installs."
      echo "-------------------------"
    fi
  '';
}
