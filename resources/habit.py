from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from db import db

from models import HabitModel
from schemas import HabitSchema, HabitUpdateSchema

blp = Blueprint("Habits", "habits", description="Operations on habits")

@blp.route("/habit/<int:habit_id>")
class Habit(MethodView):
    @jwt_required()
    @blp.response(200, HabitSchema)
    def get(self, habit_id):
        habit = HabitModel.query.get_or_404(habit_id)
        return habit

    @jwt_required()
    def delete(self, habit_id):
        habit = HabitModel.query.get_or_404(habit_id)
        db.session.delete(habit)
        db.session.commit()
        return {"message": "Habit deleted."}

    @jwt_required()
    @blp.arguments(HabitUpdateSchema)
    @blp.response(200, HabitSchema)
    def put(self, habit_data, habit_id):
        habit = HabitModel.query.get(habit_id)

        if habit:
            habit.name = habit_data["name"]
            habit.checked = habit_data["checked"]
        else:
            habit = HabitModel(id=habit_id, **habit_data)

        db.session.add(habit)
        db.session.commit()

        return habit

@blp.route("/habit")
class HabitList(MethodView):
    @jwt_required()
    @blp.response(200, HabitSchema(many=True))
    def get(self):
        return HabitModel.query.all()

    @jwt_required()
    @blp.arguments(HabitSchema)
    @blp.response(201, HabitSchema)
    def post(self, habit_data):
        habit = HabitModel(**habit_data)
        
        try:
            db.session.add(habit)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="Error when inserting habit")

        return habit