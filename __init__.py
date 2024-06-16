import os
import functools

from flask import Flask, render_template, redirect, request, session, url_for, flash, g
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

    from .models import db, User, Note

    db.init_app(app)
    migrate = Migrate(app, db) #migration instancei

    def require_login(view):
      @functools.wraps(view)
      def wrapped_view(**kwargs):#catch any keyword arg that comes in
        if not g.user: #cant look at notes unless you are logged in
          return redirect(url_for('log_in'))
        return view(**kwargs)
      return wrapped_view


    @app.before_request
    def load_user(): #get the id of user from the session and add it to g.user before any request (note reqs)
      user_id = session.get('user_id')
      if user_id:
        g.user = User.query.get(user_id)
      else:
        g.user = None



    @app.route('/sign_up', methods=('GET', 'POST'))
    def sign_up():
        if request.method == 'POST': #check method on req
          username = request.form['username']
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


    @app.route('/log_in', methods=('GET', 'POST'))
    def log_in():
      if request.method == 'POST': #check method on req
          username = request.form['username']
          password = request.form['passowrd']
          error = None

          user = User.query.filter_by(username=username).first()

          #if no user or if passoword for user doesnt exist
          if not user or not check_password_hash(user.password, password):
            error = 'Username or password are incorrect.'

          if error is None:
            session.clear() #reset the session by clearing it before login
            session['user_id'] = user.id #assignes the user an id
            return redirect(url_for('index')) #redirects to homepage after login

          flash(error, 'error')

      return render_template('log_in.html') #tells the route what needs to be displayed



    @app.route('/log_out', methods=('GET', 'DELETE'))
    def log_out():
      session.clear()
      flash('Log out successful.', 'success')
      return redirect(url_for('log_in')) #clears session and logs user out

    @app.route('/')
    def index():
      return 'Index'



    @app.route('/notes',) #reads notes on home page
    @require_login
    def note_index():
      return render_template('note_index.html', notes=g.user.notes) #get all notes from the user with this id

    @app.route('/notes/new', methods=('GET', 'POST'))
    @require_login #can only see or create notes when logged in
    def note_create():
      if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
          error = 'Title is required.'

        if not error:
          note = Note(author=g.user, title=title, body=body)
          db.session.add(note) #add note to session
          db.session.commit() #session commits note to db
          flash(f"Successfully created note: '{title}'", 'success')
          return redirect(url_for('note_index')) #return to home

        flash(error, 'error')

      return render_template('note_create.html')






    return app
