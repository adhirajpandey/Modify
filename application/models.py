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
    album = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    date_updated = db.Column(db.DateTime, nullable=False)
    rating = db.Column(db.Integer, nullable=True)

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    artist = db.Column(db.String(120), nullable=False)
    genre = db.Column(db.String(120), nullable=False)

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(120), nullable=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class PlaylistSong(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playlist = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    song = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)