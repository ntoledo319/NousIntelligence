{ pkgs }: {
  deps = [
    pkgs.graphviz
    pkgs.python311
    pkgs.python311Packages.flask
    pkgs.python311Packages.flask-login
    pkgs.python311Packages.flask-sqlalchemy
    pkgs.python311Packages.gunicorn
    pkgs.python311Packages.pip
    pkgs.python311Packages.setuptools
    pkgs.python311Packages.wheel
    pkgs.python311Packages.requests
  ];
} 