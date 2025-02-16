{ pkgs, lib, config, inputs, ... }:
let
  buildInputs = with pkgs; [
    python311Full
    # cudaPackages.cuda_cudart
    # cudaPackages.cudnn
    stdenv.cc.cc
  ];

  DJANGO_MODULE = "endo_ai";

in 
{

  # A dotenv file was found, while dotenv integration is currently not enabled.
  dotenv.enable = false;
  dotenv.disableHint = true;


  packages = with pkgs; [
    cudaPackages.cuda_nvcc
    stdenv.cc.cc
  ];

  env = {
    LD_LIBRARY_PATH = "${
      with pkgs;
      lib.makeLibraryPath buildInputs
    }:/run/opengl-driver/lib:/run/opengl-driver-32/lib";
    CONF_DIR = "./conf";
    DJANGO_DEBUG = "True";
    DJANGO_SETTINGS_MODULE = "${DJANGO_MODULE}.settings_dev";

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
    "${pkgs.uv}/bin/uv run python manage.py runserver localhost:8182";

  scripts.run-prod-server.exec =
    "${pkgs.uv}/bin/uv run daphne ${DJANGO_MODULE}.asgi:application";

  scripts.env-setup.exec = ''
    export CONF_DIR="/var/endo-ai/data"
    export DJANGO_SETTINGS_MODULE="${DJANGO_MODULE}.settings_dev"
    export DJANGO_DEBUG="True"
    export LD_LIBRARY_PATH="${
      with pkgs;
      lib.makeLibraryPath buildInputs
    }:/run/opengl-driver/lib:/run/opengl-driver-32/lib"
  '';

  scripts.init-environment.exec = ''
    uv pip install -e .
    if [ -d "endoreg-db-production/.git" ]; then
      cd endoreg-db-production && git pull && cd ..
    else
      git clone https://github.com/wg-lux/endoreg-db ./endoreg-db-production
    fi
    
    uv pip install -e endoreg-db-production/. 

    if [ -d "endoreg-db-api-production/.git" ]; then
      cd endoreg-db-api-production && git pull && cd ..
    else
      git clone https://github.com/wg-lux/endoreg-db-api ./endoreg-db-api-production
    fi

    uv pip install -e endoreg-db-api-production/.

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

  scripts.test-local-endoreg-db.exec = ''
    cd endoreg-db-production
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
    # init-environment
  '';
}
