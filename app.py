from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'FFFFDDDDSSSS'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://viktor:311991@db:3306/flask_app?charset=utf8mb4'
CORS(app, resources={r"/*": {"origins": "http://localhost:8081"}})
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)

import routes.routes

if __name__ == '__main__':
    app.run(debug=True)
