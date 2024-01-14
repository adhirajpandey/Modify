from flask import current_app as app, render_template, request, redirect, url_for, session
from application.models import User, Song, Album, Playlist
from application.database import db
import application.services as services


@app.route("/", methods = ["GET"])
@app.route("/index", methods = ["GET"])
def index():
    return render_template("index.html")

@app.route("/register", methods = ["GET", "POST"])
def user_register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        if services.input_validation(username, password):
            user = User(username=username, password=password, type='general')
            user_details = User.query.filter_by(username=username).first()
            if user_details:
                error_message = "Username already exists"
                return render_template("user_register.html", error=error_message)
            else:
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('user_login'))
        else:
            error_message = "Length of username and password should be greater than 5"
            return render_template("user_register.html", error=error_message)        

    return render_template("user_register.html")

@app.route("/login", methods = ["GET", "POST"])
def user_login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        if services.input_validation(username, password):
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                session['username'] = username
                session['type'] = user.type
                session['user_id'] = user.id
                return redirect(url_for('user_home'))
            else:
                error_message = "Invalid username or password"
                return render_template("user_login.html", error=error_message)
   
    return render_template("user_login.html")

@app.route("/logout", methods = ["GET", "POST"])
def logout():
    session.pop('username', None)
    session.pop('type', None)
    return redirect(url_for('index'))

@app.route("/admin-login", methods = ["GET"])
def admin_login():
    return render_template("admin_login.html")

@app.route("/user-home", methods = ["GET"])
def user_home():
    if 'user_id' in session:
        RATING_LIMIT = 3
        recommended_tracks = Song.query.filter(Song.rating > RATING_LIMIT).limit(10).all()
        user_playlists = Playlist.query.filter(Playlist.user_id==session['user_id']).limit(10).all()
        featured_album = Album.query.filter(Album.id==1).first()
        featured_album_songs = Song.query.filter(Song.album==1).limit(10).all()
        return render_template("user_home.html", username=session['username'], recommended_tracks=recommended_tracks, user_playlists=user_playlists, featured_album=featured_album, featured_album_songs=featured_album_songs)
    else:
        return redirect(url_for('user_login'))

@app.route("/song-details/<int:song_id>", methods=["GET"])
def song_details(song_id):
    song = Song.query.get(song_id)
    if song:
        return render_template("song_details.html", song=song)
    else:
        return render_template("index.html")

@app.route("/creator-account", methods = ["GET", "POST"])
def creator_account():
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        if user.type == 'creator':
            return redirect(url_for('creator_home'))
        else:
            if request.method == "POST":
                user.type = 'creator'
                db.session.commit()
                message = "Your account has been registered as creator account, Now redirecting to creator home page"
                return render_template("creator_register.html", message = message)
            else:
                return render_template("creator_register.html")
    else:
        return redirect(url_for('user_login'))

@app.route("/creator-home", methods = ["GET"])
def creator_home():
    if 'user_id' in session and session['type'] == 'creator':
        return render_template("creator_home.html")
    else:
        return redirect(url_for('user_login'))

@app.route("/song-upload", methods = ["GET", "POST"])
def song_upload():
    if 'user_id' in session and session['type'] == 'creator':
        albums = Album.query.filter_by(user_id=session['user_id']).all()
        if request.method == "POST":
            title = request.form.get('title')
            artist = request.form.get('artist')
            release_date = request.form.get('release-date')
            lyrics = request.form.get('lyrics')
            duration = request.form.get('duration')
            album = request.form.get('album')

            if album == "none":
                song = Song(name=title, artist=artist, duration=duration, lyrics=lyrics, release_date=release_date, user_id=session['user_id'])
            else:
                song = Song(name=title, artist=artist, duration=duration, lyrics=lyrics, album=album, release_date=release_date, user_id=session['user_id'])
            db.session.add(song)
            db.session.commit()
            message = "Song uploaded successfully, redirecting to Creator Home Page"
            return render_template("song_upload.html", albums=albums, message=message)
        else:
            return render_template("song_upload.html", albums=albums)
    else:
        return redirect(url_for('user_login'))

@app.route("/creator-dashboard", methods = ["GET"])
def creator_dashboard():
    if 'user_id' in session and session['type'] == 'creator':
        albums = Album.query.filter_by(user_id=session['user_id']).all()
        albums_count = len(albums)
        songs = Song.query.filter_by(user_id=session['user_id']).all()
        songs_count = len(songs)
        
        rating_sum = 0
        songs_with_ratings = 0

        for song in songs:
            if song.rating:
                rating_sum += song.rating
                songs_with_ratings += 1

        rating = round(rating_sum / songs_with_ratings, 1)
        return render_template("creator_dashboard.html", albums_count=albums_count, songs_count=songs_count, rating=rating, songs = songs)
    else:
        return redirect(url_for('user_login'))

@app.route("/admin-dashboard", methods = ["GET"])
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route("/admin-all-tracks", methods = ["GET"])
def admin_all_tracks():
    return render_template("admin_all_tracks.html")

@app.route("/admin-all-albums", methods = ["GET"])
def admin_all_albums():
    return render_template("admin_all_albums.html")

@app.route("/song-edit/<int:song_id>", methods = ["GET", "POST"])
def song_edit(song_id):
    if 'user_id' in session and session['type'] == 'creator':
        song_details = Song.query.filter_by(id=song_id).first()
        if request.method == "POST":
            new_title = request.form.get('title')
            new_artist = request.form.get('artist')
            new_release_date = request.form.get('release-date')
            new_lyrics = request.form.get('lyrics')
            new_duration = request.form.get('duration')
            new_album = request.form.get('album')

            song_details.name = new_title
            song_details.artist = new_artist
            song_details.release_date = new_release_date
            song_details.lyrics = new_lyrics
            song_details.duration = new_duration
            song_details.album = new_album            
            
            db.session.commit()

            message = "Song Edited Successfully, redirecting to Creator Dashboard"
            return render_template("song_edit.html", song_details=song_details, message=message)
        else:
            return render_template("song_edit.html", song_details=song_details)
    else:
        return redirect(url_for('user_login'))
    
@app.route("/profile", methods = ["GET", "POST"])
def profile():
    if 'user_id' in session:
        profile_details = User.query.filter_by(id=session['user_id']).first()
        if request.method == "POST":
            name = request.form.get('name')
            email = request.form.get('email')

            print(name, email)

            profile_details.name = name
            profile_details.email = email
            
            db.session.commit()

            message = "Profile Edited Successfully, redirecting to Creator Dashboard"
            return render_template("profile.html", profile_details=profile_details, message=message)
        else:
            return render_template("profile.html", profile_details=profile_details)
    else:
        return redirect(url_for('user_login'))
    
@app.route("/song-delete/<int:song_id>", methods = ["GET", "POST"])
def song_delete(song_id):
    if 'user_id' in session and session['type'] == 'creator':
        song_details = Song.query.filter_by(id=song_id).first()
        if request.method == "POST":
            db.session.delete(song_details)
            db.session.commit()

            message = "Song Edited Successfully, redirecting to Creator Dashboard"
            return render_template("song_delete.html", song_details=song_details, message=message)
        else:
            return render_template("song_delete.html", song_details=song_details)
    else:
        return redirect(url_for('user_login'))
     
@app.route("/creator-songs", methods = ["GET", "POST"])
def creator_songs():
    if 'user_id' in session and session['type'] == 'creator':
        songs = Song.query.filter_by(user_id=session['user_id']).all()

        return render_template("creator_songs.html",songs = songs)
    else:
        return redirect(url_for('user_login'))
    
@app.route("/creator-albums", methods = ["GET", "POST"])
def creator_albums():
    if 'user_id' in session and session['type'] == 'creator':
        albums = Album.query.filter_by(user_id=session['user_id']).all()

        return render_template("creator_albums.html",albums = albums)
    else:
        return redirect(url_for('user_login'))
    
@app.route("/album-details/<int:album_id>", methods = ["GET", "POST"])
def album_details(album_id):
    if 'user_id' in session and session['type'] == 'creator':
        album = Album.query.filter_by(id=album_id).first()
        songs = Song.query.filter_by(album=album_id).all()

        return render_template("album_details.html",album=album, songs=songs)
    else:
        return redirect(url_for('user_login'))
    
@app.route("/album-delete/<int:album_id>", methods = ["GET", "POST"])
def album_delete(album_id):
    if 'user_id' in session and session['type'] == 'creator':
        album = Album.query.filter_by(id=album_id).first()
        if request.method == "POST":
            db.session.delete(album)
            db.session.commit()

            message = "Album Deleted Successfully, redirecting to Creator Dashboard"
            return render_template("album_delete.html", album=album, message=message)
        else:
            return render_template("album_delete.html", album=album)
    else:
        return redirect(url_for('user_login'))
    
@app.route("/album-create", methods = ["GET", "POST"])
def album_create():
    if 'user_id' in session and session['type'] == 'creator':
        if request.method == "POST":
            name = request.form.get('name')
            artist = request.form.get('artist')
            genre = request.form.get('genre')

            album = Album(name=name, artist=artist, genre=genre, user_id=session['user_id'])
            db.session.add(album)
            db.session.commit()

            message = "Album Created Successfully, redirecting to Creator Dashboard"
            return render_template("album_create.html", message=message)
        else:
            return render_template("album_create.html")
    else:
        return redirect(url_for('user_login'))
    
@app.route("/album-edit/<int:album_id>", methods = ["GET", "POST"])
def album_edit(album_id):
    if 'user_id' in session and session['type'] == 'creator':
        album = Album.query.filter_by(id=album_id).first()
        if request.method == "POST":
            new_name = request.form.get('name')
            new_artist = request.form.get('artist')
            new_genre = request.form.get('genre')

            album.name = new_name
            album.artist = new_artist
            album.genre = new_genre
            
            db.session.commit()

            message = "Album Edited Successfully, redirecting to Creator Dashboard"
            return render_template("album_edit.html", album=album, message=message)
        else:
            return render_template("album_edit.html", album=album)
    else:
        return redirect(url_for('user_login'))