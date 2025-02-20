{ pkgs, lib, config, inputs, ... }:
let
  buildInputs = with pkgs; [
    python311Full
    # cudaPackages.cuda_cudart
    # cudaPackages.cudnn
    stdenv.cc.cc
  ];

  DJANGO_MODULE = "endo_ai";

  user = "admin";

  dataDir = "./data";
  importDir = "./data/import";
  importVideoDir = "${importDir}/video";
  importReportDir = "${importDir}/report";
  importLegacyAnnotationDir = "${importDir}/legacy_annotations";
  
  exportDir = "./data/export";
  exportFramesRootDir = "${exportDir}/frames";
  exportFramesSampleExportDir = "${exportFramesRootDir}/test_outputs";
  modelDir = "./data/models";

  endoregDbRepoDir = "./endoreg_db_production";
  endoregDbApiRepoDir = "./endoreg_db_api_production";
  aglFrameExtractorRepoDir = "./agl_frame_extractor";

  port = 8183;

in 
{

  # A dotenv file was found, while dotenv integration is currently not enabled.
  dotenv.enable = false;
  dotenv.disableHint = true;


  packages = with pkgs; [
    cudaPackages.cuda_nvcc
    stdenv.cc.cc
    ffmpeg_6-full
    tesseract
  ];

  env = {
    DJANGO_PSEUDO_DIR = "/home/admin/test-data";
    LD_LIBRARY_PATH = "${
      with pkgs;
      lib.makeLibraryPath buildInputs
    }:/run/opengl-driver/lib:/run/opengl-driver-32/lib";
    CONF_DIR = "./conf";
    DJANGO_DEBUG = "True";
    DJANGO_SETTINGS_MODULE = "${DJANGO_MODULE}.settings_dev";
    # SSL_CERT_FILE = "${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt";

  };

  languages.python = {
    enable = true;
    uv = {
      enable = true;
      sync.enable = true;
    };
  };

  scripts.hello.exec = "${pkgs.uv}/bin/uv run python hello.py";
  scripts.run-dev-server.exec =
    "${pkgs.uv}/bin/uv run python manage.py runserver localhost:${toString port}";

  scripts.run-prod-server.exec =
    "${pkgs.uv}/bin/uv run daphne ${DJANGO_MODULE}.asgi:application";

  scripts.env-setup.exec = ''
    export CONF_DIR="/var/endo-ai/data"
    export PSEUDO_DIR="/var/endo-ai/data"
    export DJANGO_SETTINGS_MODULE="${DJANGO_MODULE}.settings_dev"
    export DJANGO_DEBUG="True"
    export LD_LIBRARY_PATH="${
      with pkgs;
      lib.makeLibraryPath buildInputs
    }:/run/opengl-driver/lib:/run/opengl-driver-32/lib"
  '';

  scripts.init-environment.exec = ''
    ensure-dirs 

    uv pip install -e .
    
    if [ -d "${endoregDbRepoDir}/.git" ]; then
      cd ${endoregDbRepoDir} && git pull && cd ..
    else
      git clone https://github.com/wg-lux/endoreg-db ./${endoregDbRepoDir}
    fi
    
    uv pip install -e ${endoregDbRepoDir}/. 

    if [ -d "${endoregDbApiRepoDir}/.git" ]; then
      cd ${endoregDbApiRepoDir} && git pull && cd ..
    else
      git clone https://github.com/wg-lux/endoreg-db-api ./${endoregDbApiRepoDir}
    fi

    uv pip install -e ${endoregDbApiRepoDir}/.

    if [ -d "${aglFrameExtractorRepoDir}/.git" ]; then
      cd ${aglFrameExtractorRepoDir} && git pull && cd ..
    else
      git clone https://github.com/wg-lux/agl-frame-extractor ./${aglFrameExtractorRepoDir}
    fi

    uv pip install -e ${aglFrameExtractorRepoDir}/.

    devenv tasks run deploy:make-migrations
    devenv tasks run deploy:migrate
  '';

  scripts.check-psql.exec = ''
    devenv tasks run deploy:ensure-psql-user
  '';

  scripts.init-lxdb-config.exec = ''
    devenv tasks run deploy:init-conf
  '';

  scripts.init-data.exec = ''
    export DJANGO_SETTINGS_MODULE="${DJANGO_MODULE}.settings_prod"
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

    chown -R ${user} ${dataDir}
    chmod -R 700 ${dataDir}
    '';

  scripts.test-local-endoreg-db.exec = ''
    cd ${endoregDbRepoDir}
    devenv shell -i runtests
    cd ..
  '';

  scripts.install-api.exec = ''
    init-lxdb-config
    check-psql
    init-data
  '';


  tasks = {
    "deploy:init-conf".exec = "${pkgs.uv}/bin/uv run python scripts/make_conf.py";
    "deploy:ensure-psql-user".exec = "${pkgs.uv}/bin/uv run python scripts/ensure_psql_user.py";
    "deploy:make-migrations".exec = "${pkgs.uv}/bin/uv run python manage.py makemigrations";
    "deploy:migrate".exec = "${pkgs.uv}/bin/uv run python manage.py migrate";
    "deploy:load-base-db-data".exec = "${pkgs.uv}/bin/uv run python manage.py load_base_db_data";
    "deploy:collectstatic".exec = "${pkgs.uv}/bin/uv run python manage.py collectstatic --noinput";
    "test:gpu".exec = "${pkgs.uv}/bin/uv run python gpu-check.py";
    "dev:runserver".exec = "${pkgs.uv}/bin/uv run python manage.py runserver";
    "prod:runserver".exec = "${pkgs.uv}/bin/uv run daphne ${DJANGO_MODULE}.asgi:application -b 172.16.255.142 -p 8123";
  };

  processes = {
    django.exec = "run-dev-server";
    silly-example.exec = "while true; do echo hello && sleep 10; done";
    # django.exec = "${pkgs.uv}/bin/uv run python manage.py runserver 127.0.0.1:8123";
  };

  enterShell = ''
    . .devenv/state/venv/bin/activate
    init-environment
  '';
}
