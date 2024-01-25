from flask import current_app as app, render_template, request, redirect, url_for, session
from application.models import User, Song, Album, Playlist, PlaylistSong, RatingSong
from application.database import db
import application.utils as utils
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')

# Primary Routes
@app.route("/", methods = ["GET"])
@app.route("/index", methods = ["GET"])
def index():
    return render_template("index.html")

@app.route("/register", methods = ["GET", "POST"])
def user_register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        if utils.input_validation(username, password):
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

        if utils.input_validation(username, password):
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                session['username'] = username
                session['type'] = user.type
                session['user_id'] = user.id

                liked_songs_playlist = Playlist.query.filter_by(name='Liked Songs', user_id=user.id).first()
                if not liked_songs_playlist:
                    playlist = Playlist(name='Liked Songs', description='Liked Songs', user_id=user.id)
                    db.session.add(playlist)
                    db.session.commit()
                return redirect(url_for('user_home'))
            else:
                error_message = "Invalid username or password"
                return render_template("user_login.html", error=error_message)
   
    return render_template("user_login.html")

@app.route("/logout", methods = ["GET", "POST"])
def logout():
    session.pop('username', None)
    session.pop('type', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route("/admin-login", methods = ["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        if utils.input_validation(username, password):
            user = User.query.filter_by(username=username, password=password, type="admin").first()
            if user:
                session['username'] = username
                session['type'] = user.type
                session['user_id'] = user.id
                return redirect(url_for('admin_dashboard'))
            else:
                error_message = "Invalid username or password"
                return render_template("admin_login.html", error=error_message)
        
    return render_template("admin_login.html")


# General User Routes
@app.route("/user-home", methods = ["GET"])
def user_home():
    if 'user_id' in session:
        if session['type'] != 'admin':
            all_songs = Song.query.all()
            all_songs_ids = [song.id for song in all_songs]

            average_ratings = utils.fetch_songs_average_ratings(all_songs_ids)
            recommended_tracks_ids = sorted(average_ratings, key=average_ratings.get, reverse=True)[:10]

            recommended_tracks = []
            for id in recommended_tracks_ids:
                recommended_tracks.append(Song.query.filter_by(id=id).first())

            user_playlists = Playlist.query.filter(Playlist.user_id==session['user_id']).limit(10).all()
            featured_album_id = 2
            featured_album = Album.query.filter_by(id=featured_album_id).first()
            featured_album_songs = Song.query.filter_by(album=featured_album_id).limit(10).all()
            return render_template("user_home.html", 
                                username=session['username'], 
                                recommended_tracks=recommended_tracks, 
                                user_playlists=user_playlists, 
                                featured_album=featured_album, 
                                featured_album_songs=featured_album_songs,
                                featured_album_id=featured_album_id
                                )
        else:
            return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('user_login'))

@app.route("/profile", methods = ["GET", "POST"])
def profile():
    if 'user_id' in session:
        profile_details = User.query.filter_by(id=session['user_id']).first()
        if request.method == "POST":
            name = request.form.get('name')
            email = request.form.get('email')

            profile_details.name = name
            profile_details.email = email
            
            db.session.commit()

            message = "Profile Updated Successfully!! Now, redirecting to home page."
            return render_template("profile.html", profile_details=profile_details, message=message)
        else:
            return render_template("profile.html", profile_details=profile_details)
    else:
        return redirect(url_for('user_login'))
         
@app.route("/playlist-create", methods = ["GET", "POST"])
def playlist_create():
    if 'user_id' in session:
        if request.method == "POST":
            name = request.form.get('name')
            description = request.form.get('descriptiont')

            playlist = Playlist(name=name, description=description, user_id=session['user_id'])
            db.session.add(playlist)
            db.session.commit()

            message = "Playlist Created Successfully!! Now, redirecting to home."
            return render_template("playlist_create.html", message=message)
        else:
            return render_template("playlist_create.html")
    else:
        return redirect(url_for('user_login'))
        
@app.route("/playlist-details/<int:playlist_id>", methods=["GET"])
def playlist_details(playlist_id):
    if 'user_id' in session:
        playlist = Playlist.query.filter_by(id=playlist_id).first()
        playlist_songs_ids = PlaylistSong.query.filter_by(playlist=playlist_id).all()
        playlist_songs = []
        for playlist_song in playlist_songs_ids:
            song = Song.query.filter_by(id=playlist_song.song).first()
            playlist_songs.append(song)

        return render_template("playlist_details.html", playlist=playlist, playlist_songs=playlist_songs)
    else:
        return redirect(url_for('user_login'))
    
@app.route("/playlist-remove", methods=["POST"])
def playlist_remove():
    if 'user_id' in session:
        song_id = request.form.get('song_id')
        playlist_id = request.form.get('playlist_id')

        playlist_song = PlaylistSong.query.filter_by(song=song_id, playlist=playlist_id).first()
        if playlist_song:
            db.session.delete(playlist_song)
            db.session.commit()

        return redirect(url_for('playlist_details', playlist_id=playlist_id))
    else:
        return redirect(url_for('user_login'))

@app.route("/recommended-tracks", methods=["GET"])
def recommended_tracks():
    if 'user_id' in session:
        all_songs = Song.query.all()
        all_songs_ids = [song.id for song in all_songs]

        average_ratings = utils.fetch_songs_average_ratings(all_songs_ids)
        recommended_tracks_ids = sorted(average_ratings, key=average_ratings.get, reverse=True)[:20]

        recommended_tracks = []
        for id in recommended_tracks_ids:
            recommended_tracks.append(Song.query.filter_by(id=id).first())

        return render_template("recommended_tracks.html", recommended_tracks=recommended_tracks)
    else:
        return redirect(url_for('user_login'))
    
@app.route("/search-results", methods=["GET", "POST"])
def search_results():
    if 'user_id' in session:
        if request.method == "GET":
            search_query = request.args.get('query')
            song_search_results = Song.query.filter(Song.name.like("%" + search_query + "%")).all()
            album_search_results = Album.query.filter(Album.name.like("%" + search_query + "%")).all()
            playlist_search_results = Playlist.query.filter(Playlist.name.like("%" + search_query + "%")).all()
            return render_template("search_results.html",
                                   song_search_results=song_search_results,
                                   album_search_results=album_search_results,
                                   playlist_search_results=playlist_search_results
                                   )
        else:
            return render_template("search_results.html")
    else:
        return redirect(url_for('user_login'))
    
@app.route("/user-album-details/<int:album_id>", methods=["GET"])
def user_album_details(album_id):
    if 'user_id' in session:
        album = Album.query.filter_by(id=album_id).first()
        album_songs = Song.query.filter_by(album=album_id).all()

        return render_template("user_album_details.html", album=album, album_songs=album_songs)
    else:
        return redirect(url_for('user_login'))


# Song Routes
@app.route("/song-upload", methods = ["GET", "POST"])
def song_upload():
    if 'user_id' in session and session['type'] == 'creator':
        creator_albums = Album.query.filter_by(user_id=session['user_id']).all()
        if request.method == "POST":
            title = request.form.get('title')
            artist = request.form.get('artist')
            release_date = request.form.get('release-date')
            lyrics = request.form.get('lyrics')
            duration = request.form.get('duration')
            album = request.form.get('album')
            file = request.files['file']

            if file:
                filename = utils.get_filename()
                file.save(filename)
            else:
                filename = "static/images/songs/0.jpg"

            if album == "none":
                song = Song(name=title, artist=artist, duration=duration, lyrics=lyrics, album=-1, release_date=release_date, user_id=session['user_id'], image=filename)
            else:
                song = Song(name=title, artist=artist, duration=duration, lyrics=lyrics, album=album, release_date=release_date, user_id=session['user_id'], image=filename)
            
            
            db.session.add(song)
            db.session.commit()
            message = "Song Uploaded Successfully!! Now, redirecting to creator dashboard."
            return render_template("song_upload.html", creator_albums=creator_albums, message=message)
        else:
            return render_template("song_upload.html", creator_albums=creator_albums)
    else:
        return redirect(url_for('user_login'))
    
@app.route("/song-details/<int:song_id>", methods=["GET"])
def song_details(song_id):
    if 'user_id' in session:
        song = Song.query.filter_by(id=song_id).first()
        song_album=Album.query.filter_by(id=song.album).first()
        song_rating = utils.fetch_song_average_rating(song_id)

        DEFAULT_USER_RATING = 3
        user_song_rating = DEFAULT_USER_RATING
        user_song_rating = RatingSong.query.filter_by(song_id=song_id, user_id=session['user_id']).first()
        if user_song_rating:
            user_song_rating = user_song_rating.rating

        user_liked_songs_playlist_id = Playlist.query.filter_by(name='Liked Songs', user_id=session['user_id']).first().id
        all_playlists = Playlist.query.filter(Playlist.user_id==session['user_id']).all()

        playlist_without_song = []

        for playlist in all_playlists:
            a = PlaylistSong.query.filter_by(song=song_id, playlist=playlist.id).first()
            if not a:
                playlist_without_song.append(playlist)

        if PlaylistSong.query.filter_by(song=song_id, playlist=user_liked_songs_playlist_id).first():
            liked = True
        else:
            liked = False
        if song:
            return render_template("song_details.html",
                                    song=song,
                                    song_liked=liked, 
                                    all_playlists=playlist_without_song, 
                                    user_song_rating=user_song_rating, 
                                    song_rating=song_rating,
                                    song_album=song_album
                                    )
        else:
            return redirect(url_for('user_home'))
    else:
        return redirect(url_for('user_login'))

@app.route("/song-like/<int:song_id>", methods=["POST"])
def song_like(song_id):
    if 'user_id' in session:
        song_liked = request.form.get('song_liked')
        playlist_id = Playlist.query.filter_by(name='Liked Songs', user_id=session['user_id']).first().id 
        playlist_song = PlaylistSong.query.filter_by(song=song_id, playlist=playlist_id).first()

        if song_liked == 'False':
            if not playlist_song:
                playlist_song = PlaylistSong(song=song_id, playlist=playlist_id)
                db.session.add(playlist_song)
        else:
            if playlist_song:
                db.session.delete(playlist_song)

        db.session.commit()

        return redirect(url_for('song_details', song_id=song_id))
    else:
        return redirect(url_for('user_login'))
    
@app.route("/song-playlist/", methods=["POST"])
def song_playlist():
    if 'user_id' in session:
        song_id = request.form.get('song_id')
        playlist_id = request.form.get('playlist')

        playlist_song = PlaylistSong(song=song_id, playlist=playlist_id)
        db.session.add(playlist_song)

        db.session.commit()

        return redirect(url_for('song_details', song_id=song_id))
    else:
        return redirect(url_for('user_login'))

@app.route("/song-edit/<int:song_id>", methods = ["GET", "POST"])
def song_edit(song_id):
    if 'user_id' in session and session['type'] == 'creator':
        song_details = Song.query.filter_by(id=song_id).first()
        if song_details.album != -1:
                current_album_name = Album.query.filter_by(id=song_details.album).first().name
        else:
            current_album_name = "None"
        if request.method == "POST":
            new_title = request.form.get('title')
            new_artist = request.form.get('artist')
            new_release_date = request.form.get('release-date')
            new_lyrics = request.form.get('lyrics')
            new_duration = request.form.get('duration')
            new_album = request.form.get('album')

            if new_album == "none":
                new_album = -1

            song_details.name = new_title
            song_details.artist = new_artist
            song_details.release_date = new_release_date
            song_details.lyrics = new_lyrics
            song_details.duration = new_duration
            song_details.album = new_album            
            
            db.session.commit()

            message = "Song Edited Successfully!! Now, redirecting to creator dashboard."
            return render_template("song_edit.html", song_details=song_details, message=message, current_album_name=current_album_name)
        else:
            creator_albums = Album.query.filter_by(user_id=session['user_id']).all()
            return render_template("song_edit.html", song_details=song_details, creator_albums=creator_albums, current_album_name=current_album_name)
    else:
        return redirect(url_for('user_login'))
   
@app.route("/song-rating", methods=["POST"])
def song_rating():
    if 'user_id' in session:
        song_id = request.form.get('song_id')
        rating = request.form.get('rating')
        user_id = session['user_id']

        rating_song = RatingSong.query.filter_by(song_id=song_id, user_id=user_id).first()

        if not rating_song:
            rating_song = RatingSong(song_id=song_id, rating=rating, user_id=user_id)
            db.session.add(rating_song)
            db.session.commit()
        else:
            rating_song.rating = rating
            db.session.commit()

        return redirect(url_for('song_details', song_id=song_id))
    else:
        return redirect(url_for('user_login'))

@app.route("/song-delete", methods=["POST"])
def song_delete():
    if 'user_id' in session:
        if session['type'] == 'admin' or session['type'] == 'creator':
            song_id = request.form.get('song_id')
            song = Song.query.filter_by(id=song_id).first()
            
            if song:
                db.session.delete(song)
                db.session.commit()
            if session['type'] == 'creator':
                return redirect(url_for('creator_songs'))
            else:
                return redirect(url_for('admin_all_tracks'))
        else:
            return redirect(url_for('user_home'))
    else:
        return redirect(url_for('admin_login'))

@app.route("/song-flag", methods=["POST"])
def song_flag():
    if 'user_id' in session:
        if session['type'] == 'admin':
            song_id = request.form.get('song_id')
            song = Song.query.filter_by(id=song_id).first()

            if song:
                song.flagged = 1
                db.session.commit()

            return redirect(url_for('admin_all_tracks'))
        else:
            return redirect(url_for('user_home'))
    else:
        return redirect(url_for('admin_login')) 


# Creator Routes
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
                session['type'] = 'creator'
                message = "Account Registered as Creator Successfully!! Now, redirecting to creator dashboard."
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

@app.route("/creator-dashboard", methods = ["GET"])
def creator_dashboard():
    if 'user_id' in session and session['type'] == 'creator':
        albums = Album.query.filter_by(user_id=session['user_id']).all()
        albums_count = len(albums)
        
        songs = Song.query.filter_by(user_id=session['user_id']).all()
        songs_count = len(songs)

        song_ids = [song.id for song in songs]

        songs_avg_ratings = []
                
        for id in song_ids:
            rating_sum = 0
            rating_song = RatingSong.query.filter_by(song_id=id).all()
            for rating in rating_song:
                rating_sum += rating.rating
            if len(rating_song) > 0:
                song_rating = round(rating_sum / len(rating_song), 1)
            else:
                song_rating = 0
            songs_avg_ratings.append(song_rating)

        avg_rating = 0
        if len(songs_avg_ratings) > 0:
            avg_rating = round(sum(songs_avg_ratings) / len(songs_avg_ratings), 1)
        else:
            avg_rating = 0
        return render_template("creator_dashboard.html", albums_count=albums_count, songs_count=songs_count, rating=avg_rating, songs=songs)
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
    if 'user_id' in session:
        if session['type'] == 'creator' or session['type'] == 'admin':
            album = Album.query.filter_by(id=album_id).first()
            songs = Song.query.filter_by(album=album_id).all()

            return render_template("album_details.html",album=album, songs=songs)
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

            message = "Album Created Successfully!! Now, redirecting to creator home."
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

            message = "Album Edited Successfully!! Now, redirecting to your albums."
            return render_template("album_edit.html", album=album, message=message)
        else:
            return render_template("album_edit.html", album=album)
    else:
        return redirect(url_for('user_login'))
    
@app.route("/album-delete", methods=["POST"])
def album_delete():
    if 'user_id' in session:
        if session['type'] == 'admin' or session['type'] == 'creator':
            album_id = request.form.get('album_id')
            album = Album.query.filter_by(id=album_id).first()
            
            if album:
                db.session.delete(album)
                db.session.commit()
            
            # set albumid as -1 in songs
            songs = Song.query.filter_by(album=album_id).all()
            for song in songs:
                song.album = -1
                db.session.commit()

            if session['type'] == 'creator':
                return redirect(url_for('creator_albums'))
            else:                   
                return redirect(url_for('admin_all_albums'))
        else:
            return redirect(url_for('user_home'))
    else:
        return redirect(url_for('admin_login'))

@app.route("/album-flag", methods=["POST"])
def album_flag():
    if 'user_id' in session:
        if session['type'] == 'admin':
            album_id = request.form.get('album_id')
            album = Album.query.filter_by(id=album_id).first()

            if album:
                album.flagged = 1
                db.session.commit()
            

            return redirect(url_for('admin_all_albums'))
        else:
            return redirect(url_for('user_home'))
    else:
        return redirect(url_for('admin_login'))
    

# Admin Routes
@app.route("/admin-dashboard", methods = ["GET"])
def admin_dashboard():
    if session.get("user_id"):
        if session['type'] == 'admin':
            creator_accounts = User.query.filter_by(type='creator').all()
            creator_accounts_count = len(creator_accounts)

            general_accounts = User.query.filter_by(type='general').all()
            general_accounts_count = len(general_accounts)

            all_songs = Song.query.all()
            all_songs_count = len(all_songs)

            all_albums = Album.query.all()
            all_albums_count = len(all_albums)

            all_genres = Album.query.with_entities(Album.genre).distinct().all()
            all_genres_count = len(all_genres)
            
            return render_template("admin_dashboard.html",
                                    creator_accounts_count=creator_accounts_count, 
                                    general_accounts_count=general_accounts_count,
                                    all_songs_count=all_songs_count,
                                    all_albums_count=all_albums_count,
                                    all_genres_count=all_genres_count
                                )
        else:
            return redirect(url_for('user_home'))
    else:
        return redirect(url_for('admin_login'))

@app.route("/admin-all-tracks", methods = ["GET"])
def admin_all_tracks():
    if session.get("user_id"):
        if session['type'] == 'admin':
            # get those album ids from song table which are not null
            all_album_ids = Song.query.with_entities(Song.album).distinct().all()
            all_albums = {}
            
            for album in all_album_ids:
                if album[0] != -1:
                    album = Album.query.filter_by(id=album[0]).first()
                    all_albums[album.id] = album.name

            all_tracks = {}
            
            for album in all_album_ids:
                tracks = Song.query.filter_by(album=album[0]).all()
                all_tracks[all_albums.get(album[0])] = tracks            

            return render_template("admin_all_tracks.html",
                                    all_tracks=all_tracks
                                )
        else:
            return redirect(url_for('user_home'))
    else:
        return redirect(url_for('admin_login'))

@app.route("/admin-all-albums", methods = ["GET"])
def admin_all_albums():
    if session.get("user_id"):
        if session['type'] == 'admin':
            # get all albums categorised in genres
            all_genres = Album.query.with_entities(Album.genre).distinct().all()
            all_albums = {}
            for genre in all_genres:
                albums = Album.query.filter_by(genre=genre[0]).all()
                all_albums[genre[0]] = albums            


            return render_template("admin_all_albums.html",
                                    all_albums=all_albums
                                )
        else:
            return redirect(url_for('user_home'))
    else:
        return redirect(url_for('admin_login'))
    
@app.route("/admin-search-results", methods = ["GET"])
def admin_search_results():
    if 'user_id' in session:
        if session['type'] == 'admin':
            if request.method == "GET":
                search_query = request.args.get('query')
                song_search_results = Song.query.filter(Song.name.like("%" + search_query + "%")).all()
                album_search_results = Album.query.filter(Album.name.like("%" + search_query + "%")).all()
                playlist_search_results = Playlist.query.filter(Playlist.name.like("%" + search_query + "%")).all()
                return render_template("admin_search_results.html",
                                    song_search_results=song_search_results,
                                    album_search_results=album_search_results,
                                    playlist_search_results=playlist_search_results
                                    )
            else:
                return render_template("admin_search_results.html")
        else:
            return redirect(url_for('user_home'))
    else:
        return redirect(url_for('admin_login'))

@app.route("/admin-more-analytics", methods = ["GET"])
def admin_more_analytics():
    if 'user_id' in session:
        if session['type'] == 'admin':
            if request.method == "GET":
                utils.create_charts()
                return render_template("admin_more_analytics.html")
            else:
                return render_template("admin_more_analytics.html")
        else:
            return redirect(url_for('user_home'))
    else:
        return redirect(url_for('admin_login'))
    