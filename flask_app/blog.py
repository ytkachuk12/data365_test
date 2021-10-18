"""Flask Blueprint file

    - POST / users - adds a new user to the database. id is assigned automatically and returned in response
    - GET / users / <user_id> - returns data for a specific user, or 404 if there is no such user in the database
    - GET / users / <user_id> / tweets - returns a list of tweets for the user
    - POST / tweets - adds a new tweet to the database. created_at for a tweet is set automatically.
    id is assigned automatically and returned in response
"""

import logging
import time
from flask import (
    Blueprint, g, request, jsonify, json, current_app
    )
from werkzeug.exceptions import abort, HTTPException, InternalServerError


from flask_app.db import get_db

bp = Blueprint('blog', __name__)

# add logger. check log info in record.log file in root app folder (cd .. for change directory)
logging.basicConfig(filename='record.log', level=logging.DEBUG,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


@bp.before_request
def before_request():
    """Launch before any request"""
    # get start request time
    g.start = time.time()


@bp.teardown_request
def teardown_request(exception=None):
    """Launch after any request"""
    # count processing time
    current_app.logger.info("Request processing time: %.5fs" % (time.time() - g.start))


@bp.route('/users', methods=['POST'])
def add_user():
    """Add a new user into db
    :return json {user_id: }"""
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
    :return json {tweet_id: }"""
    # take input json
    content = request.get_json()

    db = get_db()

    if not request.json:
        abort(400, 'Incorrect json data')

    # insert tweet data in db if user exist
    # check is user exist
    user = db.execute(
        'SELECT id FROM users WHERE id = ?', (content['author_id'],)
    ).fetchone()
    # insert tweet data in db
    if user:
        last_id = db.execute(
            'INSERT INTO tweet (author_id, body) VALUES (?, ?)',
            (content['author_id'], content['body'],)
        )
        db.commit()
    else:
        abort(404, f"User {content['author_id']} did not register.")

    return jsonify({'tweet_id': last_id.lastrowid})


@bp.route('/users/tweets/', methods=['GET'])
def get_tweets():
    """Get all tweets from db by user id
    :return json[{"tweet_id": ,"author_id": ,"body": , "created_at": },{}...]"""
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

    # change sqlite3.Row object to list[{of dicts}]
    response = []
    for tweet in tweets:
        response.append(dict(tweet))
    return jsonify(response)


@bp.errorhandler(HTTPException)
def handle_exception(exception):
    """Return JSON errors."""
    if not isinstance(exception, HTTPException):
        exception = InternalServerError()
    # start with the correct headers and status code from the error
    response = exception.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": exception.code,
        "name": exception.name,
        "description": exception.description,
    })
    response.content_type = "application/json"
    return response
