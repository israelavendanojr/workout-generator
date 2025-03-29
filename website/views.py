from flask import Blueprint, render_template, request
from flask_login import login_required, current_user


views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/generate-workout', methods=['GET', 'POST'])
def generate_plan():
    if request.method == "POST":
        days_available = request.form.get("days_available")
        session_length = request.form.get("session_length")
        goal = request.form.get("goal")
        sex = request.form.get("sex")
        equipment = request.form.getlist("equipment")

        print(days_available, session_length, goal, sex, equipment)

    return render_template("generate_plan.html")
