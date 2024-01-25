from application.database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(32), nullable=False, default='general')
    name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), nullable=True)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    artist = db.Column(db.String(120), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    lyrics = db.Column(db.String(120), nullable=True)
    album = db.Column(db.Integer, db.ForeignKey('album.id', name='fk_song_album'), nullable=True)
    release_date = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_song_user'), nullable=False)
    flagged = db.Column(db.Integer, nullable=False, default=0)
    image = db.Column(db.String(120), nullable=True)

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    artist = db.Column(db.String(120), nullable=False)
    genre = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_album_user'), nullable=False)
    flagged = db.Column(db.Integer, nullable=False, default=0)

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(120), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_playlist_user'), nullable=False)

class PlaylistSong(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playlist = db.Column(db.Integer, db.ForeignKey('playlist.id', name='fk_playlistsong_playlist'), nullable=False)
    song = db.Column(db.Integer, db.ForeignKey('song.id', name='fk_playlistsong_song'), nullable=False)

class RatingSong(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rating = db.Column(db.Integer, nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id', name='fk_playlistsong_song'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_playlistsong_user'), nullable=False)