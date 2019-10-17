import os
from flask import request, send_from_directory, Blueprint, current_app, session, jsonify, url_for, redirect
from imagerepository import db
from werkzeug.utils import secure_filename

from imagerepository.models import User, Image

bp = Blueprint('image', __name__, url_prefix='/images')

ACCEPTED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

def accepted_filename(filename):
    split_filename = filename.split('.')
    if len(split_filename) != 2:
        return False
    [name, extension] = split_filename
    return extension.lower() in ACCEPTED_EXTENSIONS and name


@bp.errorhandler(400)
@bp.route('/', methods=['POST'])
def upload_image():
    if 'user_id' not in session:
        return 'Need to login to upload images', 400

    user_id = session['user_id']
    user = User.query.get(user_id)

    if 'file' not in request.files:
        return 'Missing file', 400
    file = request.files['file']

    if file and accepted_filename(file.filename):
        filename = secure_filename(file.filename)

        old_img = Image.query.filter_by(filename=filename, owner_id=user.id).first()
        if old_img:
            # Overwriting this image
            db.session.delete(old_img)

        private = False
        if 'private' in request.args:
            private = True

        image = Image(owner=user, filename=filename, private=private)
        db.session.add(image)
        db.session.commit()

        user_dir = os.path.join('imagerepository', current_app.config['UPLOAD_FOLDER'], str(image.owner.username))
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        file.save(os.path.join(user_dir, filename))

        response = {
            'message': 'Successfully uploaded',
            'filename': image.filename,
            'image_id': image.id
        }

        return jsonify(response), 201

    return 'File missing or name not acceptable', 400


@bp.errorhandler(400)
@bp.route('/', methods=['GET'])
def view_images():
    images = Image.query.filter_by(private=False).all()

    if 'user_id' in session:
        # Logged in, include their private photos
        user_id = session['user_id']
        user = User.query.get(user_id)

        private_imgs = Image.query.filter_by(owner=user, private=True).all()
        images = images + private_imgs


    img_urls = []
    for image in images:
        img_urls.append(url_for('image.view_image', image_id=image.id))

    return jsonify(img_urls), 200


@bp.errorhandler(400)
@bp.route('/mine/', methods=['GET'])
def view_personal_images():
    if 'user_id' not in session:
        return 'Need to login to view personal photos', 400

    user_id = session['user_id']
    user = User.query.get(user_id)

    if 'private' in request.args:
        images = Image.query.filter_by(owner=user, private=True)

    else:
        images = Image.query.filter_by(owner=user)

    img_urls = []
    for image in images:
        img_urls.append(url_for('image.view_image', image_id=image.id))

    return jsonify(img_urls), 200


@bp.errorhandler(400)
@bp.route('/mine/', methods=['DELETE'])
def delete_personal_images():
    if 'user_id' not in session:
        return 'Need to login to delete personal photos', 400

    user_id = session['user_id']
    user = User.query.get(user_id)

    images = Image.query.filter_by(owner=user).all()

    user_dir = os.path.join('imagerepository', current_app.config['UPLOAD_FOLDER'], str(user.username))

    if os.path.exists(user_dir):

        for image in images:
            filepath = os.path.join(user_dir, image.filename)
            os.remove(filepath)
            db.session.delete(image)

        db.session.commit()
        os.rmdir(user_dir)

    return redirect(url_for('image.view_personal_images'))


@bp.errorhandler(400)
@bp.errorhandler(401)
@bp.errorhandler(404)
@bp.route('/<int:image_id>', methods=['GET'])
def view_image(image_id):
    image = Image.query.get(image_id)

    if not image:
        return 'Image does not exist', 404

    if image.private:
        if 'user_id' not in session:
            return 'Need to login to view private photos', 400
        user_id = session['user_id']

        if user_id != image.owner_id:
            return 'Attempting to access photo without authorization', 401

    img_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(image.owner.username))
    return send_from_directory(img_dir, image.filename)


@bp.errorhandler(400)
@bp.errorhandler(401)
@bp.route('/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    if 'user_id' not in session:
        return 'Need to login to delete photos', 400

    user_id = session['user_id']

    image = Image.query.get(image_id)

    if not image:
        return 'Image does not exist', 404

    if image.owner_id != user_id:
        return 'Unauthorized to delete others photos', 401

    user_dir = os.path.join('imagerepository', current_app.config['UPLOAD_FOLDER'], str(image.owner.username))

    if os.path.exists(user_dir):
        filepath = os.path.join(user_dir, image.filename)
        os.remove(filepath)

        # Delete directory if this was the last image in it
        if not os.listdir(user_dir):
            os.rmdir(user_dir)

    db.session.delete(image)
    db.session.commit()

    return redirect(url_for('image.view_personal_images'))
