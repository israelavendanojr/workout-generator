from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_required, current_user
import json
from website import db
from website.models import SavedPlan, Exercise, ExerciseRole, SavedDay, SavedExercise, Note
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
    try:
        # Get data from form
        split_name = request.form.get('split_name')
        plan_data = request.form.get('plan_data')
        
        print("Received data:", {
            'split_name': split_name,
            'plan_data': plan_data
        })
        
        if not split_name or not plan_data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        try:
            plan = json.loads(plan_data)
            print("Parsed plan:", plan)
        except json.JSONDecodeError as e:
            print("JSON decode error:", str(e))
            return jsonify({'error': 'Invalid plan data format'}), 400
        
        # Create new saved plan
        saved_plan = SavedPlan(
            split_name=split_name,
            user_id=current_user.id
        )
        db.session.add(saved_plan)
        db.session.flush()  # Get the ID of the new plan
        
        # Create saved days with order
        for index, day in enumerate(plan['days']):
            saved_day = SavedDay(
                saved_plan_id=saved_plan.id,
                day_name=day['name'],
                order=index
            )
            db.session.add(saved_day)
            db.session.flush()  # Get the ID of the new day
            
            # Create saved exercises
            for exercise_index, exercise in enumerate(day['exercises']):
                saved_exercise = SavedExercise(
                    saved_day_id=saved_day.id,
                    exercise_id=exercise['exercise_id'],
                    name=exercise['name'],
                    sets=exercise['sets'],
                    start_reps=exercise['start_reps'],
                    end_reps=exercise['end_reps'],
                    to_failure=exercise.get('to_failure', False),
                    order=exercise_index
                )
                db.session.add(saved_exercise)
        
        db.session.commit()
        return redirect(url_for('views.saved_plans'))

    except Exception as e:
        print("Unexpected error:", str(e))
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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

    return render_template("saved_plans.html", 
                         user=current_user, 
                         plans=plans, 
                         exercises_by_role=exercises_by_role_serializable, 
                         exercise_roles=exercise_roles)

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
    notes_data = request.form.getlist('notes[]')  # Get notes as a list

    # Get the plan
    saved_plan = SavedPlan.query.get_or_404(plan_id)
    if saved_plan.user_id != current_user.id:
        flash("Unauthorized plan access", "danger")
        return redirect(url_for('views.saved_plans'))

    # Find the saved exercise to update
    saved_exercise = SavedExercise.query.get_or_404(old_exercise_id)
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

    # Update notes
    # First, delete all existing notes
    for note in saved_exercise.notes:
        db.session.delete(note)
    
    # Then add new notes
    for index, note_content in enumerate(notes_data):
        if note_content.strip():  # Only add non-empty notes
            note = Note(
                content=note_content.strip(),
                saved_exercise_id=saved_exercise.id,
                order=index
            )
            db.session.add(note)

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
    def get_saved_plan(plan_id):
        plan = SavedPlan.query.get_or_404(plan_id)
        if plan.user_id != current_user.id:
            raise PermissionError("Unauthorized plan access")
        return plan

    def get_saved_day(day_id, plan_id):
        day = SavedDay.query.get_or_404(day_id)
        if day.saved_plan_id != plan_id:
            raise ValueError("Day does not belong to plan")
        return day

    def get_exercise(exercise_id):
        return Exercise.query.get_or_404(exercise_id)

    try:
        # Get and validate form data
        plan_id = int(request.form.get('plan_id', 0))
        day_id = int(request.form.get('day_id', 0))
        exercise_id = int(request.form.get('exercise_id', 0))
        sets = int(request.form.get('sets', 3))
        start_reps = int(request.form.get('start_reps', 8))
        end_reps = int(request.form.get('end_reps', 12))

        if not all([plan_id, day_id, exercise_id]):
            flash("Missing required fields", "danger")
            return redirect(url_for('views.saved_plans'))

        saved_plan = get_saved_plan(plan_id)
        saved_day = get_saved_day(day_id, plan_id)
        exercise = get_exercise(exercise_id)

        # Get the current highest order for this day
        max_order = db.session.query(db.func.max(SavedExercise.order)).filter_by(saved_day_id=day_id).scalar() or 0

        # Create new saved exercise
        new_exercise = SavedExercise(
            saved_day_id=day_id,
            exercise_id=exercise.id,
            name=exercise.name,
            sets=sets,
            start_reps=start_reps,
            end_reps=end_reps,
            to_failure=False,  
            order=max_order + 1  # Add to the end of the list
        )

        db.session.add(new_exercise)
        db.session.commit()
        flash("Exercise added successfully!", "success")
        return redirect(url_for('views.saved_plans'))

    except ValueError as e:
        print(f"ValueError: {str(e)}")  # Debug: Print the specific ValueError
        flash("Invalid input data", "danger")
        return redirect(url_for('views.saved_plans'))
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # Debug: Print any other errors
        flash(f"Error adding exercise: {str(e)}", "danger")
        return redirect(url_for('views.saved_plans'))


@views.route('/delete_exercise', methods=['POST'])
@login_required
def delete_exercise():
    try:
        # Get the saved exercise ID from the form
        saved_exercise_id = int(request.form.get('exercise_id', 0))
        if not saved_exercise_id:
            flash("Invalid exercise ID", "danger")
            return redirect(url_for('views.saved_plans'))

        # Get the saved exercise and verify it exists
        saved_exercise = SavedExercise.query.get_or_404(saved_exercise_id)
        
        # Get the day and plan to verify ownership
        saved_day = saved_exercise.workout_day
        saved_plan = saved_day.saved_plan

        # Verify the plan belongs to the current user
        if saved_plan.user_id != current_user.id:
            flash("Unauthorized access", "danger")
            return redirect(url_for('views.saved_plans'))

        # Get the day_id and order for reordering
        day_id = saved_day.id
        deleted_order = saved_exercise.order

        # Delete the exercise
        db.session.delete(saved_exercise)

        # Update the order of remaining exercises
        remaining_exercises = SavedExercise.query.filter(
            SavedExercise.saved_day_id == day_id,
            SavedExercise.order > deleted_order
        ).all()

        for exercise in remaining_exercises:
            exercise.order -= 1

        db.session.commit()
        flash("Exercise deleted successfully!", "success")
        return redirect(url_for('views.saved_plans'))

    except ValueError:
        flash("Invalid input data", "danger")
        return redirect(url_for('views.saved_plans'))
    except Exception as e:
        flash(f"Error deleting exercise: {str(e)}", "danger")
        return redirect(url_for('views.saved_plans'))

@views.route('/reorder_exercise', methods=['POST'])
@login_required
def reorder_exercise():
    try:
        # Get the exercise ID, new order, and new day ID from the form
        exercise_id = int(request.form.get('exercise_id', 0))
        new_order = int(request.form.get('new_order', 0))
        new_day_id = int(request.form.get('new_day_id', 0))
        
        if not all([exercise_id, new_day_id, new_order >= 0]):
            return jsonify({"success": False, "error": "Invalid input data"}), 400

        # Get the exercise and verify ownership
        saved_exercise = SavedExercise.query.get_or_404(exercise_id)
        old_day = saved_exercise.workout_day
        old_plan = old_day.saved_plan

        # Verify the plan belongs to the current user
        if old_plan.user_id != current_user.id:
            return jsonify({"success": False, "error": "Unauthorized access"}), 403

        # Get the new day and verify it belongs to the same plan
        new_day = SavedDay.query.get_or_404(new_day_id)
        if new_day.saved_plan_id != old_plan.id:
            return jsonify({"success": False, "error": "Cannot move exercise to different plan"}), 400

        # Get all exercises in the new day
        day_exercises = SavedExercise.query.filter_by(saved_day_id=new_day_id).order_by(SavedExercise.order).all()
        
        # Remove the exercise from its current position
        if old_day.id == new_day_id:
            day_exercises.remove(saved_exercise)
        
        # Insert it at the new position
        day_exercises.insert(new_order, saved_exercise)
        
        # Update all orders and the day_id
        for i, exercise in enumerate(day_exercises):
            exercise.order = i
            if exercise.id == saved_exercise.id:
                exercise.saved_day_id = new_day_id

        db.session.commit()
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@views.route('/rename-day', methods=['POST'])
@login_required
def rename_day():
    try:
        day_id = int(request.form.get('day_id', 0))
        new_name = request.form.get('new_name')

        if not day_id or not new_name:
            flash("Invalid input data", "danger")
            return redirect(url_for('views.saved_plans'))

        # Get the day and verify ownership
        saved_day = SavedDay.query.get_or_404(day_id)
        saved_plan = saved_day.saved_plan

        if saved_plan.user_id != current_user.id:
            flash("Unauthorized access", "danger")
            return redirect(url_for('views.saved_plans'))

        # Update the day name
        saved_day.day_name = new_name
        db.session.commit()
        flash("Day renamed successfully!", "success")
        return redirect(url_for('views.saved_plans'))

    except Exception as e:
        flash(f"Error renaming day: {str(e)}", "danger")
        return redirect(url_for('views.saved_plans'))

@views.route('/reorder_day', methods=['POST'])
@login_required
def reorder_day():
    try:
        # Get the day ID and new order from the form
        day_id = int(request.form.get('day_id', 0))
        new_order = int(request.form.get('new_order', 0))
        
        if not all([day_id, new_order >= 0]):
            return jsonify({"success": False, "error": "Invalid input data"}), 400

        # Get the day and verify ownership
        saved_day = SavedDay.query.get_or_404(day_id)
        saved_plan = saved_day.saved_plan

        if saved_plan.user_id != current_user.id:
            return jsonify({"success": False, "error": "Unauthorized access"}), 403

        # Get all days in the plan
        plan_days = SavedDay.query.filter_by(saved_plan_id=saved_plan.id).order_by(SavedDay.order).all()
        
        # Remove the day from its current position
        plan_days.remove(saved_day)
        
        # Insert it at the new position
        plan_days.insert(new_order, saved_day)
        
        # Update all orders
        for i, day in enumerate(plan_days):
            day.order = i

        db.session.commit()
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
