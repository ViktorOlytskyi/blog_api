FROM python:3.10.0-slim-buster

WORKDIR /application
RUN apt-get update && apt-get install -y pkg-config libmariadb-dev-compat gcc
RUN pip install flask Flask-SQLAlchemy Flask-Login Jinja2 mysqlclient mysql-connector-python pymysql cryptography flask-wtf Flask-Migrate Flask-Script flask_session Flask-JWT-Extended flask_bcrypt

CMD ./wait-for-it.sh db:3306 -- flask run --host=0.0.0.0 --port=8082