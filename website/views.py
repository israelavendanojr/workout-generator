from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_required, current_user
import json
from website import db
from website.models import SavedPlan, Exercise, ExerciseRole, SavedDay, SavedExercise
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
    user = current_user
    split_name = request.form.get('split_name')
    plan_data_raw = request.form.get('plan_data')

    try:
        new_plan_data = json.loads(plan_data_raw)
    except json.JSONDecodeError:
        flash("Invalid plan data.", "danger")
        return redirect(url_for('views.generated_plans'))

    # Create new saved plan
    new_plan = SavedPlan(
        split_name=split_name,
        user_id=user.id
    )
    db.session.add(new_plan)
    db.session.flush()  # Get the new plan's ID

    # Create saved days and exercises
    for day_data in new_plan_data['days']:
        saved_day = SavedDay(
            saved_plan_id=new_plan.id,
            day_name=day_data['name']
        )
        db.session.add(saved_day)
        db.session.flush()  # Get the new day's ID

        # Add exercises for this day
        for i, exercise_data in enumerate(day_data['exercises']):
            # Get the exercise from the database
            exercise = Exercise.query.get(exercise_data['exercise_id'])
            if exercise:  # Skip if exercise not found
                saved_exercise = SavedExercise(
                    saved_day_id=saved_day.id,
                    exercise_id=exercise.id,
                    name=exercise.name,
                    sets=exercise_data['sets'],
                    start_reps=exercise_data['start_reps'],
                    end_reps=exercise_data['end_reps'],
                    to_failure=exercise_data.get('to_failure', False),  # Default to False if not specified
                    order=i
                )
                db.session.add(saved_exercise)

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
        role_name = exercise.role.name
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

    # Find the saved exercise to update
    saved_exercise = SavedExercise.query.filter_by(id=old_exercise_id).first()
    if not saved_exercise:
        flash("Exercise not found in plan", "danger")
        return redirect(url_for('views.saved_plans'))

    # Verify the exercise belongs to the plan
    if saved_exercise.workout_day.saved_plan_id != plan_id:
        flash("Exercise does not belong to this plan", "danger")
        return redirect(url_for('views.saved_plans'))

    # Get the new exercise
    new_exercise = Exercise.query.get(new_exercise_id)
    if not new_exercise:
        flash("New exercise not found", "danger")
        return redirect(url_for('views.saved_plans'))

    # Update the saved exercise
    saved_exercise.exercise_id = new_exercise.id
    saved_exercise.name = new_exercise.name
    saved_exercise.sets = new_sets
    saved_exercise.start_reps = new_start_reps
    saved_exercise.end_reps = new_end_reps

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
