from flask import jsonify
from flask import current_app as app
from application.models import User
from application.database import db


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    d = {}
    for user in users:
        d[user.id] = {'username': user.username, 'email': user.email}
    return jsonify({'users': d})

@app.route('/add', methods=['GET'])
def add_users():
    id = 1
    username = 'test'
    email = 'adsad@adsa.ada'
    user = User(id=id, username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Add user'})