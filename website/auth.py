from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html", user="Israel", boolean=True)

@auth.route('/logout')
def logout():
    return "<h1>logout</h1>"

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # get info from form
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # validate info from form
        if len(username) < 3:
            flash('Username must be 3 or more characters', category='error')
        elif len(password1) < 5:
            flash('Password must be greater than 5 or more characters', category='error')
        elif password1 != password2:
            flash('Passwords do not match', category='error')
        else:
            # add user to database
            flash('Account successfully created!', category='success')
            pass
        
    # elif request.method == 'GET':
    #     pass
    return render_template("sign_up.html")
