from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_required, current_user
import json
from website import db
from website.models import SavedPlan, Exercise, ExerciseRole
from collections import defaultdict
from website.generate_plan import generate_plans

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
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
            # flash('Generated workout plan!', category='success')
            
            # session to store across requests, convert to json bc session can only store simple types
            session['workout_plans'] = json.dumps(workout_plans)
            flash("Succesfully generated plan!", "success")

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


@views.route('/save_plan', methods=['POST'])
@login_required
def save_plan():
    user = current_user  # however you're handling users
    split_name = request.form.get('split_name')
    plan_data_raw = request.form.get('plan_data')

    try:
        new_plan_data = json.loads(plan_data_raw)
    except json.JSONDecodeError:
        flash("Invalid plan data.", "danger")
        return redirect(url_for('views.generated_plans'))

    # Serialize in a normalized way to compare plans
    def normalize(plan):
        return json.dumps(plan, sort_keys=True)

    normalized_new = normalize(new_plan_data)

    # Check if this normalized plan already exists
    for existing_plan in user.saved_plans:  # adjust depending on your ORM structure
        existing_data = existing_plan.get_plan_data()  # or existing_plan.plan_data
        if normalize(existing_data) == normalized_new:
            flash("This plan is already saved.", "info")
            return redirect(url_for('views.saved_plans'))

    # If it's unique, save it
    new_plan = SavedPlan(
        user_id=user.id,
        split_name=split_name,
        plan_data=new_plan_data
    )
    db.session.add(new_plan)
    db.session.commit()

    flash("Plan saved successfully!", "info")
    return redirect(url_for('views.saved_plans'))

@views.route('/saved_plans')
@login_required
def saved_plans():
    plans = SavedPlan.query.filter_by(user_id=current_user.id).all()

    # Group exercises by role for dropdown options
    exercises = Exercise.query.all()
    exercises_by_role = defaultdict(list)
    exercises_by_role_serializable = defaultdict(list)

    for exercise in exercises:
        role_name = exercise.role.name  # turn ExerciseRole into plain string
        exercises_by_role_serializable[role_name].append({
            'id': exercise.id,
            'name': exercise.name,
        })

    exercise_roles = ExerciseRole.query.all()

    return render_template("saved_plans.html", user=current_user, plans=plans, exercises_by_role=exercises_by_role_serializable, exercise_roles=exercise_roles)

@views.route('/delete_plan/<int:plan_id>', methods=['POST'])
@login_required
def delete_plan(plan_id):
    # find saved plan by ID
    plan = SavedPlan.query.get_or_404(plan_id)

    if plan.user_id != current_user.id:
        flash("You cannot delete plans you do not own.", "error")
        return redirect(url_for('views.saved_plans'))

    # delete plan
    db.session.delete(plan)
    db.session.commit()

    flash("Plan deleted successfully!", category="success")
    return redirect(url_for('views.saved_plans'))

@views.route('/swap-exercise', methods=['POST'])
@login_required
def swap_exercise():
    plan_id = int(request.form['plan_id'])
    old_exercise_id = int(request.form['exercise_id'])
    new_exercise_id = int(request.form['new_exercise_id'])

    # Optional: custom reps/sets input
    new_sets = int(request.form.get('sets', 3))
    new_start_reps = int(request.form.get('start_reps', 8))
    new_end_reps = int(request.form.get('end_reps', 12))

    # Get the plan
    saved_plan = SavedPlan.query.get_or_404(plan_id)
    if saved_plan.user_id != current_user.id:
        flash("Unauthorized plan access", "danger")
        return redirect(url_for('views.saved_plans'))

    # Load JSON and find the old exercise
    plan_data = saved_plan.get_plan_data()
    found = False

    for day in plan_data['days']:
        for i, exercise in enumerate(day['exercises']):
            if exercise['id'] == old_exercise_id:
                new_exercise = Exercise.query.get(new_exercise_id)
                if not new_exercise:
                    flash("New exercise not found", "danger")
                    return redirect(url_for('views.saved_plans'))

                # Update exercise info in JSON
                day['exercises'][i] = {
                    "name": new_exercise.name,
                    "sets": new_sets,
                    "start_reps": new_start_reps,
                    "end_reps": new_end_reps,
                    "role": {
                        "id": new_exercise.role.id,
                        "name": new_exercise.role.name
                    },
                    "id": new_exercise.id
                }
                found = True
                break

    if not found:
        flash("Exercise not found in plan", "danger")
        return redirect(url_for('views.saved_plans'))

    # Save updated JSON back to the plan
    saved_plan.plan = json.dumps(plan_data)
    db.session.commit()

    flash("Changes saved successfully!", "success")
    return redirect(url_for('views.saved_plans'))

@views.route('/rename-plan', methods=['POST'])
@login_required
def rename_plan():
    plan_id = request.form.get('plan_id')
    new_name = request.form.get('new_name')

    plan = SavedPlan.query.filter_by(id=plan_id, user_id=current_user.id).first()
    if plan:
        plan.split_name = new_name
        db.session.commit()
        flash('Plan renamed successfully!', category='success')
    else:
        flash('Plan not found or access denied.', category='error')

    return redirect(url_for('views.saved_plans'))

@views.route('/add_exercise', methods=['POST'])
@login_required
def add_exercise():
    plan_id = request.form.get('plan_id')
    exercise_role = request.form.get('exercise_role')
    exercise_id = request.form.get('exercise_id')
