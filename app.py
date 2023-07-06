from flask import Flask, jsonify, render_template, url_for, redirect, session, request, flash
from flask_smorest import Api
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token
import os
from flask_jwt_extended import jwt_manager, JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from blocklist import BLOCKLIST
import models

from models import UserModel
from models import HabitModel
from schemas import UserSchema, HabitSchema
from resources.user import UserLogin

from resources.habit import blp as HabitBlueprint
from resources.user import blp as UserBlueprint
from forms import LoginForm, RegisterForm

def create_app(db_url=None): 
    app = Flask(__name__)
    load_dotenv()

    #app.config["SERVER_NAME"] = "http://127.0.0.1:5000"

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
    api.register_blueprint(HabitBlueprint)
    api.register_blueprint(UserBlueprint)

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
        return redirect(url_for('loginUser'))

    @app.route('/register_user', methods=["GET","POST"])
    def registerUser():
        form = RegisterForm()
        if form.validate_on_submit():
            hashed_pwd = pbkdf2_sha256.hash(form.pwd.data)
            user = UserModel(username = form.username.data, pwd = hashed_pwd)
            try:
                db.session.add(user)
                db.session.commit()
            except IntegrityError:
                abort(400, message="User with that name alredy exists.")
            except SQLAlchemyError:
                abort(500, message="Cant add user.")
            print(user)
            return redirect(url_for('loginUser'))
        return render_template("register_page.html", form=form)

    @app.route('/login_user', methods=["GET","POST"])
    def loginUser():
        form = LoginForm()
        if form.validate_on_submit():
            user = UserModel.query.filter(UserModel.username == form.username.data).first()
            if user and pbkdf2_sha256.verify(form.pwd.data, user.pwd):
                login_user(user)
                print("Form data: ", form.data)
                session['access_token'] = create_access_token(identity=user.id)
                return redirect(url_for('dashboard'))
        return render_template('login_page.html', form=form)

    def is_logged_in():
        return 'access_token' in session

    @app.route('/dashboard', methods=['GET', 'POST'])
    def dashboard():
        if is_logged_in():
            user_name = current_user.username
            user_id = current_user.id
            habits = HabitModel.query.filter_by(user_id=user_id).all()

            if request.method == 'POST':
                if 'delete' in request.form:
                    habit_id = request.form.get('habit_id')
                    habit = HabitModel.query.get(habit_id)
                    if habit and habit.user_id == user_id:
                        db.session.delete(habit)
                        db.session.commit()
                
                elif 'update' in request.form:
                    habit_id = request.form.get('habit_id')
                    checked = request.form.get('checked')
                    habit = HabitModel.query.get(habit_id)
                    if habit and habit.user_id == user_id:
                        habit.checked = checked
                        db.session.commit()

                elif 'add' in request.form:
                    habit_name = request.form.get('habit_name')
                    new_habit = HabitModel(name=habit_name, checked='No', user_id=user_id)
                    db.session.add(new_habit)
                    db.session.commit()

                return redirect(url_for('dashboard'))

            return render_template('dashboard.html', habits=habits, user_name=user_name)
        else:
            return redirect(url_for('loginUser'))

    @app.route('/logout', methods=['GET', 'POST'])
    @login_required
    def logout_button():
        logout_user()
        session.pop('access_token', None)
        return redirect(url_for('loginUser'))

    return app