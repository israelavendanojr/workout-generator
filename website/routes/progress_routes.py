from flask import Blueprint, render_template
from flask_login import login_required, current_user
from website.services.progress_service import get_user_progression

progress_routes = Blueprint('progress_routes', __name__)

@progress_routes.route('/progress')
@login_required
def progress():
    progression_data = get_user_progression(current_user.id)
    return render_template("progress.html", user=current_user, progression=progression_data)
