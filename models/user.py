from db import db
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

class UserModel(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pwd = db.Column(db.String(256), unique=False, nullable=False)

    habits = db.relationship("HabitModel", back_populates="user", lazy="dynamic", cascade="all, delete")