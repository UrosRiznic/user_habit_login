from db import db

class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pwd = db.Column(db.String(256), unique=False, nullable=False)

    habits = db.relationship("HabitModel", back_populates="user", lazy="dynamic", cascade="all, delete")