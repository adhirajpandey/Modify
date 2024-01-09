from flask import current_app as app, render_template, request, redirect, url_for
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
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('user_login'))
        else:
            error_message = "Invalid username or password"
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
                return redirect(url_for('index'))
            else:
                error_message = "Invalid username or password"
                return render_template("user_login.html", error=error_message)
   
    return render_template("user_login.html")

@app.route("/admin-login", methods = ["GET"])
def admin_login():
    return render_template("admin_login.html")

@app.route("/user-home", methods = ["GET"])
def user_home():
    return render_template("user_home.html")

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

@app.route("/creator-account", methods = ["GET"])
def creator_account():
    # if already creator account, redirect to creator home to directly upload songs else open creator registration page
    return render_template("creator_register.html")

@app.route("/creator-home", methods = ["GET"])
def creator_home():
    # if already creator account, redirect to creator home to directly upload songs else open creator registration page
    return render_template("creator_home.html")

@app.route("/song-upload", methods = ["GET"])
def song_upload():
    # if already creator account, redirect to creator home to directly upload songs else open creator registration page
    return render_template("song_upload.html")

@app.route("/creator-dashboard", methods = ["GET"])
def creator_dashboard():
    return render_template("creator_dashboard.html")

@app.route("/admin-dashboard", methods = ["GET"])
def admin_dashboard():
    # if already creator account, redirect to creator home to directly upload songs else open creator registration page
    return render_template("admin_dashboard.html")