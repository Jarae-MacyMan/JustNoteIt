from flask_sqlalchemy import SQLAlchemy
from mistune import markdown

#instance of the database
db = SQLAlchemy() #connects to the db

#create user class
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, server_default=db.func.now()) #inserts the current time
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    #when user is updated changes to current time
    notes = db.relationship('Note', backref='author', lazy=True)
    #references the notes class, notes class will backreference to user with the attribute author

#note class
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text) #text instead of string so it can be longer
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(),server_onupdate=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #references user class with the foreignKey

    @property #create a method that doesnt have to be called
    def body_html(self):
        return markdown(self.body)
