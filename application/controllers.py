from flask import current_app as app, render_template, request, redirect, url_for, session
from application.models import User
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
    if 'username' in session:
        return render_template("user_home.html", username=session['username'], type=session['type'])
    else:
        return redirect(url_for('user_login'))

@app.route("/song-details", methods = ["GET"])
def song_details():
    temp_song_dict = {
        "song_id": 1,
        "song_name": "Full Song Name",
        "song_artist": "Artist Name",
        "song_album": "album1",
        "song_genre": "genre1",
        "song_year": 2021,
        "song_length": 3.5,
        "song_rating": 4.5,
        "song_listens": 100
    }

    return render_template("song_details.html", song=temp_song_dict)

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
    if 'user_id' in session:
        return render_template("creator_home.html")
    else:
        return redirect(url_for('user_login'))

@app.route("/song-upload", methods = ["GET"])
def song_upload():
    if 'user_id' in session:
        return render_template("song_upload.html", username=session['username'], type=session['type'])
    else:
        return redirect(url_for('user_login'))

@app.route("/creator-dashboard", methods = ["GET"])
def creator_dashboard():
    return render_template("creator_dashboard.html")

@app.route("/admin-dashboard", methods = ["GET"])
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route("/admin-all-tracks", methods = ["GET"])
def admin_all_tracks():
    return render_template("admin_all_tracks.html")

@app.route("/admin-all-albums", methods = ["GET"])
def admin_all_albums():
    return render_template("admin_all_albums.html")
