from flask import Blueprint, render_template, request

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
        
    elif request.method == 'GET':
        pass
    return render_template("sign_up.html")
