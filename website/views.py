from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_required, current_user
import json
from website import db
from website.models import WorkoutSplit, WorkoutDay, split_day_association, Exercise, ExerciseRole, day_role_association, SavedPlan, ExerciseType, Equipment
from collections import defaultdict
import random

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

        # validate preferences
        if days_available < 1 or 6 < days_available:
            flash('Days per week must be within 2-6', category='error')
        elif len(equipment) < 1:
            flash('Must fill equipment field', category='error')
        else:
            workout_plans = generate_plans(days_available, equipment, approach, see_plans, bodyweight_exercises)
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

    return render_template("saved_plans.html", user=current_user, plans=plans, exercises_by_role=exercises_by_role_serializable)

@views.route('/debug_saved_plans')
@login_required
def debug_saved_plans():
    plans = SavedPlan.query.filter_by(user_id=current_user.id).all()
    for plan in plans:
        print("\n", plan.split_name)
        print("\nRaw plan field in DB:", plan.plan)  # Check raw stored data
        print("\nDecoded plan_data:", json.loads(plan.plan))  # Ensure it's valid JSON
    
    return "Check console for debug output"

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

# all methods regarding generation logic for plans

def get_workout_splits(days_available):
    """Get all workout splits for the given number of days."""
    return WorkoutSplit.query.filter_by(days_per_week=days_available).all()

def get_ordered_roles(day):
    """Get ordered exercise roles for a workout day."""
    return (
        db.session.query(ExerciseRole)
        .join(day_role_association)
        .filter(day_role_association.c.workout_day_id == day.id)
        .order_by(day_role_association.c.order)
        .all()
    )

def get_suitable_exercises(role, equipment):
    """Get exercises that match the role and available equipment."""
    exercises = (
    db.session.query(Exercise)
    .join(Exercise.equipment)
    .filter(Equipment.name.in_(equipment))
    .filter(Exercise.role == role)
    .all()
    )
    return exercises

def determine_sets_and_reps(exercise, approach):
    """Determine sets and reps based on exercise type and approach."""
    roll = random.randint(1, 2)
    sets = 0
    start_reps = 0
    end_reps = 0

    if approach == "low_volume":
        if exercise.type == ExerciseType.COMPOUND:
            if roll == 1:
                sets, start_reps, end_reps = 2, 4, 6
            else:
                sets, start_reps, end_reps = 2, 6, 8
        elif exercise.type == ExerciseType.ISOLATION:
            if roll == 1:
                sets, start_reps, end_reps = 2, 6, 8
            else:
                sets, start_reps, end_reps = 1, 8, 10
    elif approach == "moderate_volume":
        if exercise.type == ExerciseType.COMPOUND:
            if roll == 1:
                sets, start_reps, end_reps = 3, 6, 10
            else:
                sets, start_reps, end_reps = 3, 8, 12
        elif exercise.type == ExerciseType.ISOLATION:
            if roll == 1:
                sets, start_reps, end_reps = 2, 8, 10
            else:
                sets, start_reps, end_reps = 3, 8, 12
    elif approach == "high_volume":
        if exercise.type == ExerciseType.COMPOUND:
            if roll == 1:
                sets, start_reps, end_reps = 4, 8, 12
            else:
                sets, start_reps, end_reps = 3, 10, 15
        elif exercise.type == ExerciseType.ISOLATION:
            if roll == 1:
                sets, start_reps, end_reps = 3, 8, 12
            else:
                sets, start_reps, end_reps = 3, 10, 15

    return sets, start_reps, end_reps

def create_exercise_info(exercise, role, sets, start_reps, end_reps, to_failure=False):
    """Create exercise information dictionary."""
    return {
        "name": exercise.name,
        "sets": sets,
        "start_reps": start_reps,
        "end_reps": end_reps,
        "role": {
            "id": role.id,
            "name": role.name
        },
        "id": exercise.id,
        "toFailure": to_failure
    }

def create_null_exercise_info(role):
    """Create null exercise information when no suitable exercise is found."""
    return {
        "name": f"No suitable exercise for {role.name} found",
        "sets": 0,
        "start_reps": 0,
        "end_reps": 0,
        "role": None,
        "toFailure": None
    }

def generate_day_plan(day, equipment, approach, bodyweight_exercises):
    """Generate plan for a single workout day."""
    day_info = {
        "name": day.name,
        "exercises": []
    }

    ordered_roles = get_ordered_roles(day)
    
    # Add bodyweight to equipment if specified
    if bodyweight_exercises != "Absent":
        equipment = equipment + ["Bodyweight"]

    for role in ordered_roles:
        exercises = get_suitable_exercises(role, equipment)
        
        if exercises:
            random_exercise = random.choice(exercises)
            sets, start_reps, end_reps = determine_sets_and_reps(random_exercise, approach)
            
            # Handle bodyweight progression
            to_failure = (random_exercise.equipment == "Bodyweight" and 
                         bodyweight_exercises == "Bodyweight")
            
            exercise_info = create_exercise_info(
                random_exercise, role, sets, start_reps, end_reps, to_failure
            )
        else:
            exercise_info = create_null_exercise_info(role)
            
        day_info["exercises"].append(exercise_info)
    
    return day_info

def generate_plans(days_available, equipment, approach, see_plans, bodyweight_exercises):
    """Generate workout plans based on user preferences."""
    workout_plans = []
    workout_splits = get_workout_splits(days_available)
    
    for split in workout_splits:
        plan = {
            "split_name": split.name,
            "days": []
        }
        
        for day in split.workout_days:
            day_info = generate_day_plan(day, equipment, approach, bodyweight_exercises)
            plan["days"].append(day_info)
        
        workout_plans.append(plan)
        
        if see_plans == "No":
            break
    
    return workout_plans
