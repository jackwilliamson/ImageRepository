from flask import Blueprint, request, session
from imagerepository.models import User
from imagerepository import db
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.errorhandler(400)
@bp.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        return 'Missing username or password', 400

    if User.query.filter_by(username=username).all():
        return 'Existing username', 400

    new_user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()

    session.clear()
    session['user_id'] = new_user.id

    return 'Successfully registered', 200



@bp.errorhandler(401)
@bp.errorhandler(400)
@bp.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        return 'Missing username or password', 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return 'User does not exist', 400

    if not check_password_hash(user.password_hash, password):
        return 'Incorrect password', 401

    session.clear()
    session['user_id'] = user.id

    return 'Successfully logged in', 200

@bp.route('/logout')
def logout():
    session.clear()
    return 'Logged out', 200