{ pkgs, lib, config, inputs, ... }:
let
  buildInputs = with pkgs; [
    python311Full
    # cudaPackages.cuda_cudart
    # cudaPackages.cudnn
    stdenv.cc.cc
  ];

  DJANGO_MODULE = "endo_ai";

  host = "localhost";
  port = "8183";

  dataDir = "data";
  importDir = "${dataDir}/import";
  importVideoDir = "${importDir}/video";
  importReportDir = "${importDir}/report";
  importLegacyAnnotationDir = "${importDir}/legacy_annotations";
  
  exportDir = "${dataDir}/export";
  exportFramesRootDir = "${exportDir}/frames";
  exportFramesSampleExportDir = "${exportFramesRootDir}/test_outputs";
  modelDir = "${dataDir}/models";

  # endoregDbRepoDir = "endoreg_db_production";
  # endoregDbApiRepoDir = "${workingDir}/endoreg_db_api_production";
  # aglFrameExtractorRepoDir = "${workingDir}/agl_frame_extractor";


  # customTasks = ( 
    
    # import ./devenv/tasks/default.nix ({
    #   inherit config pkgs lib;
    # })
  # );

in 
{

  # A dotenv file was found, while dotenv integration is currently not enabled.
  dotenv.enable = true;
  dotenv.disableHint = false;

  # shell = lib.mkForce pkgs.zsh;

  packages = with pkgs; [
    cudaPackages.cuda_nvcc
    stdenv.cc.cc
    # ffmpeg_6-full
    ffmpeg-headless.bin
    tesseract
    pkgs.zsh
  ];

  env = {
    BASE_API_URL = "http://127.0.0.1:8000";  #  API URL,Change this to the new URL, need to cross check with any other url
    LD_LIBRARY_PATH = "${
      with pkgs;
      lib.makeLibraryPath buildInputs
    }:/run/opengl-driver/lib:/run/opengl-driver-32/lib";
    CONF_DIR = "./conf";
  };

  languages.python = {
    enable = true;
    uv = {
      enable = true;
      sync.enable = true;
    };
  };

  scripts.set-prod-settings.exec = "${pkgs.uv}/bin/uv run python scripts/set_production_settings.py";
  scripts.set-dev-settings.exec = "${pkgs.uv}/bin/uv run python scripts/set_development_settings.py";
  scripts.export-env-file.exec = "export $(cat .env | xargs)";

  scripts.env-setup.exec = ''
    export DJANGO_SETTINGS_MODULE="${DJANGO_MODULE}.settings_dev"
    export DJANGO_DEBUG="True"
    export LD_LIBRARY_PATH="${
      with pkgs;
      lib.makeLibraryPath buildInputs
    }:/run/opengl-driver/lib:/run/opengl-driver-32/lib"
  '';

  scripts.run-dev-server.exec = ''
    set-dev-settings
    echo "Running dev server"
    echo "Host: ${host}"
    echo "Port: ${port}"
    ${pkgs.uv}/bin/uv run python manage.py runserver ${host}:${port}
  '';

  scripts.run-prod-server.exec = ''
    init-env
    set-prod-settings
    export-env-file
    ${pkgs.uv}/bin/uv run daphne ${DJANGO_MODULE}.asgi:application -p ${port}
  '';

  scripts.transcode-videos-in-dir.exec = ''
      ./scripts/transcode_videos.sh
    '';
  scripts.demo-summary.exec = ''
    python scripts/summary_after_demo_pipe.py
  '';
  scripts.demo-pipe.exec = ''
    ./scripts/demo_pipe.sh
    demo-summary
  '';

  scripts.check-psql.exec = ''
    devenv tasks run deploy:ensure-psql-user
  '';

  scripts.init-env.exec =''
    ensure-dirs 
    uv pip install -e .
    init-data
  
    init-lxdb-config

  '';

  scripts.init-lxdb-config.exec = ''
    devenv tasks run deploy:init-conf
  '';

  scripts.init-data.exec = ''
    devenv tasks run deploy:make-migrations
    devenv tasks run deploy:migrate
    devenv tasks run deploy:load-base-db-data
  '';

  scripts.ensure-dirs.exec = ''
    mkdir -p ${dataDir}
    mkdir -p ${importDir}
    mkdir -p ${importVideoDir}
    mkdir -p ${importReportDir}
    mkdir -p ${exportDir}
    mkdir -p ${modelDir}
    mkdir -p ${importLegacyAnnotationDir}
    mkdir -p ${exportFramesRootDir}


    chmod -R 700 ${dataDir}
    '';

  scripts.export-nix-vars.exec = ''
    cat > .devenv-vars.json << EOF
    {
      "DJANGO_MODULE": "${DJANGO_MODULE}",
      "HOST": "${host}",
      "PORT": "${port}",
      "DATA_DIR": "${dataDir}",
      "IMPORT_DIR": "${importDir}",
      "EXPORT_DIR": "${exportDir}",
      "MODEL_DIR": "${modelDir}",
      "CONF_DIR": "${config.env.CONF_DIR}",
      "HOME_DIR": "$HOME",
      "WORKING_DIR": "$PWD",
      "TEST_RUN": "False",
      "TEST_RUN_FRAME_NUMBER": "1000",
      "RUST_BACKTRACE": "1",
      "DJANGO_DEBUG": "True",
      "DJANGO_FFMPEG_EXTRACT_FRAME_BATCHSIZE": "500"
    }
    EOF
    echo "Exported Nix variables to .devenv-vars.json"
  '';

  tasks = {
    "deploy:init-conf".exec = "${pkgs.uv}/bin/uv run python scripts/make_conf.py";
    # "deploy:ensure-psql-user".exec = "${pkgs.uv}/bin/uv run python scripts/ensure_psql_user.py";
    "deploy:make-migrations".exec = "${pkgs.uv}/bin/uv run python manage.py makemigrations";
    "deploy:migrate".exec = "${pkgs.uv}/bin/uv run python manage.py migrate";
    "deploy:load-base-db-data".exec = "${pkgs.uv}/bin/uv run python manage.py load_base_db_data";
    "deploy:collectstatic".exec = "${pkgs.uv}/bin/uv run python manage.py collectstatic --noinput";
    # "test:gpu".exec = "${pkgs.uv}/bin/uv run python gpu-check.py";
    "env:build" = {
      description = "Build the .env file";
      exec = "export-nix-vars && uv run env_setup.py";
    };
    "env:export" = {
      description = "Export the .env file";
      after = ["env:build"];
      exec = "export $(cat .env | xargs)";
    };
  };

  processes = {
    django.exec = "run-prod-server";
    silly-example.exec = "while true; do echo hello && sleep 10; done";
    # django.exec = "${pkgs.uv}/bin/uv run python manage.py runserver 127.0.0.1:8123";
  };

  enterShell = ''
    . .devenv/state/venv/bin/activate
    
    # Only run env setup if .env doesn't exist or is empty
    if [ ! -f .env ] || [ ! -s .env ]; then
      echo "No .env file found, generating one..."
      export-nix-vars
      uv run env_setup.py
    fi
    export $(cat .env | xargs)
  '';
}
