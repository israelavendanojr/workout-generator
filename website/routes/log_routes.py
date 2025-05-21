from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from website.services.log_services import (
    get_logged_data_for_display,
    create_logged_week_from_saved_plan,
    delete_logged_week_by_id,
    update_logged_sets_for_day
)
from website.models.generation_models import Exercise    

log_routes = Blueprint('log_routes', __name__)

@log_routes.route('/logged_plans', methods=['GET'])
@login_required
def logged_plans():
    saved_plans, logged_weeks = get_logged_data_for_display(current_user.id)
    all_exercises = Exercise.query.order_by(Exercise.name.asc()).all()
    return render_template("logged_plans.html", user=current_user, saved_plans=saved_plans, logged_weeks=logged_weeks, all_exercises=all_exercises)

@log_routes.route('/logged_plans/add_week', methods=['POST'])
@login_required
def add_logged_week():
    data = request.get_json()
    print("Received POST to /add_week with:", data)

    success, msg, status = create_logged_week_from_saved_plan(current_user.id, data.get('plan_id'))
    if not success:
        return {"error": msg}, status

    flash(msg, "success")
    return ('', 204)

@log_routes.route('/logged_plans/delete_week/<int:week_id>', methods=['POST'])
@login_required
def delete_logged_week(week_id):
    delete_logged_week_by_id(current_user.id, week_id)
    flash("Workout week deleted.", "success")
    return redirect(url_for('log_routes.logged_plans'))

@log_routes.route('/logged_plans/log_day_sets/<int:day_id>', methods=['POST'])
@login_required
def log_day_sets(day_id):
    update_logged_sets_for_day(current_user.id, day_id, request.form)
    flash("Sets logged for the day!", "success")
    return redirect(url_for('log_routes.logged_plans'))

# CRUD for logging

@log_routes.route('/logged_plans/add_exercise/<int:day_id>', methods=['POST'])
@login_required
def add_exercise_to_day(day_id):
    exercise_id = request.form.get("exercise_id")
    sets = int(request.form.get("sets", 3))
    
    from website.models.logging_models import LoggedExercise, LoggedSet
    new_ex = LoggedExercise(logged_day_id=day_id, exercise_id=exercise_id)
    db.session.add(new_ex)
    db.session.flush()
    for _ in range(sets):
        db.session.add(LoggedSet(logged_exercise_id=new_ex.id))
    db.session.commit()
    
    flash("Exercise added!", "success")
    return redirect(url_for('log_routes.logged_plans'))

@log_routes.route('/logged_plans/delete_exercise/<int:exercise_id>', methods=['POST'])
@login_required
def delete_logged_exercise(exercise_id):
    from website.models.logging_models import LoggedExercise
    ex = LoggedExercise.query.get(exercise_id)
    if ex:
        db.session.delete(ex)
        db.session.commit()
        flash("Exercise deleted!", "success")
    else:
        flash("Exercise not found.", "error")
    return redirect(url_for('log_routes.logged_plans'))
