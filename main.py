import os
from flask import Flask
from application.database import db
from application.config import Config
from flask_migrate import Migrate


def initialize_database(app):
    if not os.path.exists(os.path.join(app.config['SQLITE_DB_DIR'], app.config['SQLITE_DB_NAME'])):
        with app.app_context():
            db.create_all()

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(Config)
    
    db.init_app(app)
    app.app_context().push()

    return app


app = create_app()
initialize_database(app)
migrate = Migrate(app, db)

from application.controllers import *


if __name__ == '__main__':
    app.run()