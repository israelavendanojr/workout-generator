from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user


views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        # get preferences from form
        days_available = int(request.form.get("days_available"))
        session_length = request.form.get("session_length")
        goal = request.form.get("goal")
        equipment = request.form.getlist("equipment")

        # validate preferences
        if days_available < 1 and 6 < days_available:
            flash('Days per week must be within 1-6', category='error')
        elif session_length == None:
            flash('Session length field required', category='error')
        elif goal == None:
            flash('Goal field required', category='error')
        elif len(equipment) < 1:
            flash('Must fill equipment field', category='error')
        else:
            flash('Generated workout plan!', category='success')

    return render_template("home.html")

@views.route('/generate-workout', methods=['GET', 'POST'])
def generate_plan():

    return render_template("generate_plan.html")
