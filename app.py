from flask import Flask, jsonify, render_template, url_for, redirect
from flask_smorest import Api
import os
from flask_jwt_extended import jwt_manager, JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_sqlalchemy import SQLAlchemy
from flask.views import MethodView

from db import db
from blocklist import BLOCKLIST
import models

from models import UserModel
from schemas import UserSchema, HabitSchema

from resources.habit import blp as HabitBlueprint
from resources.user import blp as UserBlueprint
from forms import LoginForm, RegisterForm

def create_app(db_url=None): 
    app = Flask(__name__)
    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Habits REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    
    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)

    app.config["JWT_SECRET_KEY"] = "uros"
    app.config["SECRET_KEY"] = "KEY"
    jwt = JWTManager(app)   

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"


    
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )

    with app.app_context():
        #db.create_all()
        pass

    @login_manager.user_loader
    def load_user(user_id):
        return UserModel.query.get_or_404(user_id)

    @app.route("/")
    def base():
        return "Base file"

    @app.route('/home')
    def home():
        return render_template("home.html")

    @app.route('/register_user', methods=["GET","POST"])
    def registerUser():
        form = RegisterForm()
        return render_template("register_page.html", form=form)

    @app.route('/login_user', methods=["GET","POST"])
    def loginUser():
        form = LoginForm()
        return render_template('login_page.html', form=form)

    api.register_blueprint(HabitBlueprint)
    api.register_blueprint(UserBlueprint)

    return app