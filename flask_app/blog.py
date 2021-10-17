
from flask import (
    Blueprint, g, redirect, render_template, request, url_for, jsonify, json
)
from werkzeug.exceptions import abort, HTTPException, InternalServerError


from flask_app.db import get_db

bp = Blueprint('blog', __name__)


# base_dir = os.path.dirname(os.path.abspath(__file__))
# file_path = os.path.join(base_dir, "file.json")
# with open(file_path) as f:
#     data = f.read()
#     print(data)


@bp.route('/users', methods=['POST'])
def add_user():
    """Add a new user into db
    :return user_id"""
    # take input json
    content = request.get_json()

    db = get_db()

    if not request.json or not content['user_name']:
        abort(400, 'Missing username')

    # insert data in db
    try:
        # save object db when insert username
        # in order to receive user id (call .lastrowid method)
        last_id = db.execute(
            'INSERT INTO users (username) VALUES (?)',
            (content['user_name'],),

        )
    except db.IntegrityError:
        abort(400, f"User {content['user_name']} is already registered.")
    db.commit()

    return jsonify({'user_id': last_id.lastrowid})


@bp.route('/users/', methods=['GET'])
def get_user():
    """Get user info from db by id
    :return json{"user_id": ,"user_name": }"""
    # get user_id
    user_id = request.args.get('user_id')

    db = get_db()

    # get user data from db
    user = db.execute(
        'SELECT * FROM users WHERE id = ?', (user_id,)
    ).fetchone()

    if not user:
        abort(404, f"User {user_id} did not register.")

    return jsonify({'user_id': user['id'], 'user_name': user['username']})


@bp.route('/tweets', methods=['POST'])
def add_tweet():
    """Add a new tweet into db
    :return tweet_id"""
    # take input json
    content = request.get_json()

    db = get_db()

    if not request.json:
        abort(400, 'Incorrect json data')

    # insert tweet data in db
    last_id = db.execute(
        'INSERT INTO tweet (author_id, body) VALUES (?, ?)',
        (content['author_id'], content['body'],)
    )
    db.commit()

    return jsonify({'tweet_id': last_id.lastrowid})


@bp.route('/users/tweets/', methods=['GET'])
def get_tweets():
    """Get all tweets from db by user id
    :return json{"tweet_id": ,"author_id": ,"body": , "created_at": }"""
    # get user_id
    user_id = request.args.get('user_id')

    db = get_db()

    # get all tweets data from db
    tweets = db.execute(
        'SELECT tweet_id, body, created, username '
        'FROM tweet t JOIN users u ON t.author_id = u.id '
        'WHERE u.id = ? ORDER BY created DESC',
        (user_id,)
    ).fetchall()

    if not tweets:
        abort(404, f"User {user_id} did not register.")

    response = []
    for _ in tweets:
        content = {'user_name': tweets['username'], 'tweet_id': tweets['tweet_id'],
                   'body': tweets['body'], 'created': tweets['created']}
        response.append(content)
    return jsonify(response)

    # return jsonify({'user_name': tweets['username'], 'tweet_id': tweets['tweet_id'],
    #                 'body': tweets['body'], 'created': tweets['created']})


@bp.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON errors."""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response
