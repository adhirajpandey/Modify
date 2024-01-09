from application.database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(32), nullable=False, default='general')

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    artist = db.Column(db.String(120), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    lyrics = db.Column(db.String(120), nullable=True)
    album = db.Column(db.String(120), nullable=True)
    rating = db.Column(db.Integer, nullable=True)