from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from website.models import SavedPlan  # Assuming you have this model
from website import db

log_routes = Blueprint('log_routes', __name__)

@log_routes.route('/logged_plans', methods=['GET'])
@login_required
def logged_plans():
    saved_plans = SavedPlan.query.filter_by(user_id=current_user.id).all()
    return render_template("logged_plans.html", user=current_user, saved_plans=saved_plans)

@log_routes.route('/logged_plans/add_week', methods=['POST'])
@login_required
def add_logged_week():
    data = request.get_json()
    plan_id = data.get('plan_id')

    # TODO: Lookup saved plan and generate logs
    flash(f"Logged a new workout week from plan ID: {plan_id}", "success")
    return ('', 204)
