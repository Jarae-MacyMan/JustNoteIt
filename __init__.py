import os

from flask import Flask, render_template, redirect, url_for, flash
from flask_migrate import Migrate
#creates migration script to edit db
from werkzeug.security import generate_password_hash
#encrypts the password


def create_app(test_config=None):
    app = Flask(__name__) #creates flask instance
    app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY', default='dev')
    )

    if test_config is None:
         # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    from .models import db, User

    db.init_app(app)
    migrate = Migrate(app, db) #migration instance

    #signup route
    @app.route('/sign_up', methods=('GET', 'POST'))
    def sign_up():
        if request.method == 'POST': #check method on req
          username = request.from['username']
          password = request.form['passowrd']
          error = None
          
          #if user doesnt provide username passwd or unique name then error 
          if not username: 
            error = 'Username is required'
          elif not password:
            error = 'Password is required'
          elif User.query.filter_by(username=username).first(): #searches thru db to see if username exists 
            error = 'Username exists'

          if error is None:
            user = User(username=username, password=generate_password_hash(password))
            #get session from db to edit it 
            db.session.add(user) #creates user
            db.session.commit() #inserts user into db
            flash("Sign up successful! Please log in.", 'success') #displays message to user
            return redirect(url_for('log_in')) #redirect to log in page, url_for looks for a function from the string
          
          flash(error, 'error')

        return render_template('sign_up.html') #tells the route what needs to be displayed
    
    @app.route('log_in')
    def log_in():
      return "Log in"

    return app
