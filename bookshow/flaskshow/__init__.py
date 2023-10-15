from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = '5e14a40fcda83b6d909ff639f40cccb4'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['WTF_CSRF_SSL_STRICT'] = True
app.config['SESSION_COOKIE_SECURE'] = False


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)


user_login_manager = LoginManager()
user_login_manager.login_view = 'user_login'
user_login_manager.init_app(app)

admin_login_manager = LoginManager()
admin_login_manager.login_view = 'admin_login'
admin_login_manager.init_app(app)

from flaskshow import routes
