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