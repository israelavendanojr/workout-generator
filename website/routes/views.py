from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
import json
from website.services.generation_service import generate_plans

views = Blueprint('views', __name__)

@views.route('/generator', methods=['GET', 'POST'])
def generator():
    if request.method == "POST":
        # get preferences from form
        days_available = int(request.form.get("days_available"))
        equipment = request.form.getlist("equipment")
        approach = request.form.get("approach")
        see_plans = request.form.get("see_plans")
        bodyweight_exercises = request.form.get("bodyweight_exercises")
        priority_muscles_raw = request.form.get("priority_muscles")
        priority_muscles = priority_muscles_raw.split(",") if priority_muscles_raw else []
        isolation_first = request.form.get("isolation_first")
        
        # validate preferences
        if days_available < 1 or 6 < days_available:
            flash('Days per week must be within 2-6', category='error')
        elif len(equipment) < 1:
            flash('Must fill equipment field', category='error')
        else:
            workout_plans = generate_plans(days_available, equipment, approach, see_plans, bodyweight_exercises, priority_muscles, isolation_first)
            
            # session to store across requests, convert to json bc session can only store simple types
            session['workout_plans'] = json.dumps(workout_plans)
            flash("Successfully generated plan!", "success")

            return redirect(url_for('views.generated_plans'))

    return render_template("home.html", user=current_user)

@views.route('/generated_plans')
def generated_plans():
    # Retrieve the workout plan from session
    workout_plans_json = session.get('workout_plans')

    if not workout_plans_json:
        flash("No workout plan found. Please generate a plan first.", category='error')
        return redirect(url_for('views.home'))
    
    try:
        # convert back into list of dictionary for usage
        workout_plans = json.loads(workout_plans_json)
    except Exception as e:
        flash(f"Error decoding workout plans: {str(e)}", category='error')
        return redirect(url_for('views.home'))
    
    return render_template("generated_plans.html", user=current_user, plans=workout_plans)

@views.route('/')
def landing():
    return render_template("landing.html", user=current_user)
