from flask import Blueprint, request, flash, redirect, url_for, jsonify
from flask_login import login_required
from website.services.exercise_service import swap_exercise, add_exercise, delete_exercise, reorder_exercise
from website.utils.exercise_utils import validate_exercise_swap
from website.utils.plan_utils import get_saved_plan

exercise_routes = Blueprint('exercise_routes', __name__)

@exercise_routes.route('/swap-exercise', methods=['POST'])
@login_required
def swap_exercise_route():
    try:
        # Get form data
        plan_id = int(request.form['plan_id'])
        old_exercise_id = int(request.form['exercise_id'])
        new_exercise_id = int(request.form['new_exercise_id'])
        
        # Optional: custom reps/sets input
        new_sets = int(request.form.get('sets', 3))
        new_start_reps = int(request.form.get('start_reps', 8))
        new_end_reps = int(request.form.get('end_reps', 12))
        notes_data = request.form.getlist('notes[]')  # Get notes as a list
        
        # Validate the exercise belongs to the plan
        valid, result = validate_exercise_swap(old_exercise_id, plan_id)
        if not valid:
            flash(result, "danger")
            return redirect(url_for('plan_routes.saved_plans'))
        
        # Swap the exercise
        success, message = swap_exercise(old_exercise_id, new_exercise_id, new_sets, new_start_reps, new_end_reps, notes_data)
        
        if success:
            flash(message, "success")
        else:
            flash(message, "danger")
            
        return redirect(url_for('plan_routes.saved_plans'))
    except Exception as e:
        flash(f"Error swapping exercise: {str(e)}", "danger")
        return redirect(url_for('plan_routes.saved_plans'))

@exercise_routes.route('/add_exercise', methods=['POST'])
@login_required
def add_exercise_route():
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
            return redirect(url_for('plan_routes.saved_plans'))

        # Get the plan to verify ownership
        saved_plan = get_saved_plan(plan_id)
        
        # Add the exercise
        success, message = add_exercise(day_id, exercise_id, sets, start_reps, end_reps)
        
        if success:
            flash(message, "success")
        else:
            flash(message, "danger")
            
        return redirect(url_for('plan_routes.saved_plans'))
    except Exception as e:
        flash(f"Error adding exercise: {str(e)}", "danger")
        return redirect(url_for('plan_routes.saved_plans'))

@exercise_routes.route('/delete_exercise', methods=['POST'])
@login_required
def delete_exercise_route():
    try:
        # Get the saved exercise ID from the form
        saved_exercise_id = int(request.form.get('exercise_id', 0))
        if not saved_exercise_id:
            flash("Invalid exercise ID", "danger")
            return redirect(url_for('plan_routes.saved_plans'))

        # Delete the exercise
        success, message = delete_exercise(saved_exercise_id)
        
        if success:
            flash(message, "success")
        else:
            flash(message, "danger")
            
        return redirect(url_for('plan_routes.saved_plans'))
    except Exception as e:
        flash(f"Error deleting exercise: {str(e)}", "danger")
        return redirect(url_for('plan_routes.saved_plans'))

@exercise_routes.route('/reorder_exercise', methods=['POST'])
@login_required
def reorder_exercise_route():
    try:
        # Get the exercise ID, new order, and new day ID from the form
        exercise_id = int(request.form.get('exercise_id', 0))
        new_order = int(request.form.get('new_order', 0))
        new_day_id = int(request.form.get('new_day_id', 0))
        
        if not all([exercise_id, new_day_id, new_order >= 0]):
            return jsonify({"success": False, "error": "Invalid input data"}), 400

        # Reorder the exercise
        success, error = reorder_exercise(exercise_id, new_order, new_day_id)
        
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": error}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400