from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_required, current_user
import json
from website import db
from website.models import WorkoutSplit, WorkoutDay, split_day_association, Exercise, ExerciseRole, day_role_association, SavedPlan, ExerciseType



views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        # get preferences from form
        days_available = int(request.form.get("days_available"))
        equipment = request.form.getlist("equipment")
        approach = request.form.get("approach")

        # validate preferences
        if days_available < 1 or 6 < days_available:
            flash('Days per week must be within 1-6', category='error')
        elif len(equipment) < 1:
            flash('Must fill equipment field', category='error')
        else:
            workout_plans = generate_plans(days_available, equipment, approach)
            flash('Generated workout plan!', category='success')

            # session to store across requests, convert to json bc session can only store simple types
            session['workout_plans'] = json.dumps(workout_plans)
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

def generate_plans(days_available, equipment, approach):
    import random

    # Dictionary to store plan information
    workout_plans = []

    # Find workout splits
    workout_splits = WorkoutSplit.query.filter_by(days_per_week=days_available).all()
        
    # generate plan for each workout split
    for split in workout_splits:

        # insert split name into dictionary and establish workout days
        plan = {
            "split_name": split.name,
            "days": []
        }
        
        # get workout day from split
        for day in split.workout_days:
            # insert day name into dictionary and establish exercises
            day_info = {
                "name": day.name,
                "exercises": []
            }

            ordered_roles = (
                db.session.query(ExerciseRole)
                .join(day_role_association)
                .filter(day_role_association.c.workout_day_id == day.id)
                .order_by(day_role_association.c.order)  # Order by the 'order' column in the association table
                .all()
            )

            # find suitable exercises based on exercise role and equipment available
            for role in ordered_roles:
                exercises = (
                    db.session.query(Exercise)
                    .filter(Exercise.role_id == role.id)
                    .filter(Exercise.equipment.in_(equipment))
                    .all()
                )

                if exercises:
                    random_index = random.randint(0, len(exercises)-1)
                    random_exercise = exercises[random_index]
                    
                    sets = 0
                    start_reps = 0
                    end_reps = 0
                    if approach == "low_volume":
                        if random_exercise.type == "COMPOUND":
                            sets = 2
                            start_reps = 4
                            end_reps = 8
                        elif random_exercise.type == "ISOLATION":
                            sets = 1
                            start_reps = 6
                            end_reps = 8
                    elif approach == "moderate_volume":
                        if random_exercise.type == "COMPOUND":
                            sets = 3
                            start_reps = 6
                            end_reps = 10
                        elif random_exercise.type == "ISOLATION":
                            sets = 2
                            start_reps = 8
                            end_reps = 12
                    elif approach == "high_volume":
                        if random_exercise.type == "COMPOUND":
                            sets = 4
                            start_reps = 8
                            end_reps = 12
                        elif random_exercise.type == "ISOLATION":
                            sets = 3
                            start_reps = 10
                            end_reps = 15


                    # insert exercises into dictionary
                    day_info["exercises"].append({
                        "name": random_exercise.name,
                        "sets": sets,
                        "start_reps": start_reps,
                        "end_reps": end_reps
                    })
                else:
                    # insert null exercise into dictionary if none found
                    null_exercise_message = "No suitable exercise for " + role.role + " found"
                    day_info["exercises"].append({
                        "name": null_exercise_message,
                        "sets": 0,
                        "start_reps": 0,
                        "end_reps": 0
                    })

            # add workout days to current workout plan being constructed
            plan["days"].append(day_info)

        # add completed workout plan to list of generated plans
        workout_plans.append(plan)

    # return dictionary of all generated plans
    return workout_plans

@views.route('/save_plan', methods=['POST'])
@login_required
def save_plan():
    split_name = request.form.get('split_name')
    plan_data = request.form.get('plan_data')

    # Print raw received plan data for debugging
    print(f"Received plan data: {plan_data}")  # Check what's being passed from the frontend

    if not plan_data:
        flash("Missing plan data.", "error")
        return redirect(url_for('views.generated_plans'))

    # Try to load it as JSON
    try:
        plan_data = json.loads(plan_data)
    except json.JSONDecodeError as e:
        flash(f"Error decoding plan data: {str(e)}", "error")
        return redirect(url_for('views.generated_plans'))

    new_plan = SavedPlan(split_name=split_name, plan_data=plan_data, user_id=current_user.id)
    db.session.add(new_plan)
    db.session.commit()

    flash("Plan saved successfully!", "success")
    return redirect(url_for('views.generated_plans'))

@views.route('/saved_plans')
@login_required
def saved_plans():
    plans = SavedPlan.query.filter_by(user_id=current_user.id).all()
    return render_template("saved_plans.html", user=current_user, plans=plans)

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

    flash("Plan deleted successfully!", "success")
    return redirect(url_for('views.saved_plans'))