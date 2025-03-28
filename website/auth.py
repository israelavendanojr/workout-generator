from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("here")
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                # if user valid and password valid, log in
                login_user(user, remember=True)
                flash('Logged in!', category='success')
                home_page = redirect(url_for('views.home'))
                return home_page
            else:
                flash('Incorrect password, try again', category='error')
        else:
            flash('Username not found', category='error')

    return render_template("login.html", boolean=True)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    login_page = redirect(url_for('auth.login'))
    return login_page

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # get info from form
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # validate info from form
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already taken', category='error')
        elif len(username) < 3:
            flash('Username must be 3 or more characters', category='error')
        elif len(password1) < 5:
            flash('Password must be greater than 5 or more characters', category='error')
        elif password1 != password2:
            flash('Passwords do not match', category='error')
        else:
            # add user to database
            new_user = User(username=username, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(user, remember=True)

            # flash success message
            flash('Account successfully created!', category='success')
            # redirect to home page
            home_page = redirect(url_for('views.home'))
            return home_page
        

    return render_template("sign_up.html")
