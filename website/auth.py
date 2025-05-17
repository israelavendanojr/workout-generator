from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash('Logged in!', category='success')
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again', category='error')
        else:
            flash('Username not found', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already taken', category='error')
        elif len(username) < 3:
            flash('Username must be 3 or more characters', category='error')
        elif len(password1) < 5:
            flash('Password must be 5 or more characters', category='error')
        elif not password1:
            flash('Password cannot be NONE', category='error')
        elif password1 != password2:
            flash('Passwords do not match', category='error')
        else:
            new_user = User(username=username, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account successfully created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

@auth.route('/account-settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    if request.method == 'POST':
        action = request.form.get("action")

        if action == "change_username":
            new_username = request.form.get('new_username')
            password = request.form.get('password')

            if not check_password_hash(current_user.password, password):
                flash('Incorrect password', category='error')
            elif User.query.filter_by(username=new_username).first():
                flash('Username already taken', category='error')
            elif len(new_username) < 3:
                flash('Username too short', category='error')
            else:
                current_user.username = new_username
                db.session.commit()
                flash('Username updated!', category='success')

        elif action == "change_password":
            old_password = request.form.get('old_password')
            new_password1 = request.form.get('new_password1')
            new_password2 = request.form.get('new_password2')

            if not check_password_hash(current_user.password, old_password):
                flash('Incorrect old password', category='error')
            elif len(new_password1) < 5:
                flash('Password must be 5 or more characters', category='error')
            elif not new_password1:
                flash('New password cannot be NONE', category='error')
            elif new_password1 != new_password2:
                flash('New passwords do not match', category='error')
            else:
                current_user.password = generate_password_hash(new_password1, method='pbkdf2:sha256')
                db.session.commit()
                flash('Password updated successfully', category='success')

        elif action == "delete_account":
            password = request.form.get('password')
            if not check_password_hash(current_user.password, password):
                flash('Incorrect password', category='error')
            else:
                db.session.delete(current_user)
                db.session.commit()
                flash('Account deleted successfully', category='success')
                return redirect(url_for('auth.login'))

    return render_template('account_settings.html', user=current_user)
