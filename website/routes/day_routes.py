from flask import Blueprint, request, flash, redirect, url_for, jsonify
from flask_login import login_required
from website.services.day_service import add_day, rename_day, delete_day, reorder_day
from website.utils.plan_utils import get_saved_plan

day_routes = Blueprint('day_routes', __name__)

@day_routes.route('/add_day', methods=['POST'])
@login_required
def add_day_route():
    try:
        # Get and validate form data
        plan_id = int(request.form.get('plan_id', 0))
        day_name = request.form.get('day_name')

        if not plan_id or not day_name:
            flash("Missing required fields", "danger")
            return redirect(url_for('plan_routes.saved_plans'))

        # Verify plan ownership in service layer
        success, message = add_day(plan_id, day_name)
        
        if success:
            flash(message, "success")
        else:
            flash(message, "danger")
            
        return redirect(url_for('plan_routes.saved_plans'))
    except Exception as e:
        flash(f"Error adding day: {str(e)}", "danger")
        return redirect(url_for('plan_routes.saved_plans'))

@day_routes.route('/rename-day', methods=['POST'])
@login_required
def rename_day_route():
    try:
        day_id = int(request.form.get('day_id', 0))
        new_name = request.form.get('new_name')

        if not day_id or not new_name:
            flash("Invalid input data", "danger")
            return redirect(url_for('plan_routes.saved_plans'))

        # Verify ownership in service layer
        success, message = rename_day(day_id, new_name)
        
        if success:
            flash(message, "success")
        else:
            flash(message, "danger")
            
        return redirect(url_for('plan_routes.saved_plans'))
    except Exception as e:
        flash(f"Error renaming day: {str(e)}", "danger")
        return redirect(url_for('plan_routes.saved_plans'))

@day_routes.route('/delete_day', methods=['POST'])
@login_required
def delete_day_route():
    try:
        # Get the saved day ID from the form
        day_id = int(request.form.get('day_id', 0))
        if not day_id:
            flash("Invalid day ID", "danger")
            return redirect(url_for('plan_routes.saved_plans'))

        # Delete day in service layer
        success, message = delete_day(day_id)
        
        if success:
            flash(message, "success")
        else:
            flash(message, "danger")
            
        return redirect(url_for('plan_routes.saved_plans'))
    except Exception as e:
        flash(f"Error deleting day: {str(e)}", "danger")
        return redirect(url_for('plan_routes.saved_plans'))

@day_routes.route('/reorder_day', methods=['POST'])
@login_required
def reorder_day_route():
    try:
        # Get the day ID and new order from the form
        day_id = int(request.form.get('day_id', 0))
        new_order = int(request.form.get('new_order', 0))
        
        if not all([day_id, new_order >= 0]):
            return jsonify({"success": False, "error": "Invalid input data"}), 400

        # Reorder day in service layer
        success, error = reorder_day(day_id, new_order)
        
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": error}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400