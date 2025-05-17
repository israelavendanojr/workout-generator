from flask import Blueprint, request, flash, redirect, url_for, render_template, jsonify
from flask_login import login_required, current_user
from website.services.plan_service import save_workout_plan, rename_plan, delete_plan
from website.services.plan_service import get_all_user_plans, get_exercises_by_role, get_all_exercise_roles

plan_routes = Blueprint('plan_routes', __name__)

@plan_routes.route('/save_plan', methods=['POST'])
@login_required
def save_plan():
    try:
        # Get data from form
        split_name = request.form.get('split_name')
        plan_data = request.form.get('plan_data')
        
        if not split_name or not plan_data:
            flash('Missing required fields', category='error')
            return redirect(url_for('views.generated_plans'))
        
        saved_plan, error = save_workout_plan(split_name, plan_data)
        
        if saved_plan:
            flash('Plan saved successfully!', category='success')
            return redirect(url_for('plan_routes.saved_plans'))
        else:
            flash(f'Error saving plan: {error}', category='error')
            return redirect(url_for('views.generated_plans'))

    except Exception as e:
        flash(f"Unexpected error: {str(e)}", category='error')
        return redirect(url_for('views.generated_plans'))

@plan_routes.route('/saved_plans')
@login_required
def saved_plans():
    plans = get_all_user_plans()
    exercises_by_role = get_exercises_by_role()
    exercise_roles = get_all_exercise_roles()

    return render_template("saved_plans.html", 
                         user=current_user, 
                         plans=plans, 
                         exercises_by_role=exercises_by_role, 
                         exercise_roles=exercise_roles)

@plan_routes.route('/delete_plan/<int:plan_id>', methods=['POST'])
@login_required
def delete_plan_route(plan_id):
    success, message = delete_plan(plan_id)
    
    if success:
        flash(message, category="success")
    else:
        flash(message, category="error")
        
    return redirect(url_for('plan_routes.saved_plans'))

@plan_routes.route('/rename-plan', methods=['POST'])
@login_required
def rename_plan_route():
    plan_id = request.form.get('plan_id')
    new_name = request.form.get('new_name')
    
    if not plan_id or not new_name:
        flash('Missing required fields', category='error')
        return redirect(url_for('plan_routes.saved_plans'))
    
    success, message = rename_plan(plan_id, new_name)
    
    if success:
        flash(message, category='success')
    else:
        flash(message, category='error')
        
    return redirect(url_for('plan_routes.saved_plans'))