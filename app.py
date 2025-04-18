import json
from datetime import datetime, timedelta
import bcrypt
import random
import dotenv
from flask import Flask, jsonify, session, render_template, request, Response, url_for
from flask_github import GitHub
from flask_cors import cross_origin
from werkzeug.utils import redirect
from authlib.integrations.flask_client import OAuth

import authlib.oauth2.rfc6749.wrappers

from db_utils import DB

config = dotenv.dotenv_values(".env")
db = DB()
app = Flask(__name__)
app.secret_key = bcrypt.gensalt()
app.config['GITHUB_CLIENT_ID'] = config.get('GITHUB_CLIENT_ID')
app.config['GITHUB_CLIENT_SECRET'] = config.get('GITHUB_CLIENT_SECRET')
github = GitHub(app)
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=config.get('GOOGLE_CLIENT_ID'),
    client_secret=config.get('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
)

def email_valid(username: str):
    # TODO implement actual checks
    return True

def password_valid(password: str):
    # TODO implement actual checks
    return True

@app.route('/login/google')
def login_google():
    return google.authorize_redirect(url_for('auth_google', _external=True))

@app.route('/auth/google')
def auth_google():
    token = google.authorize_access_token()
    id_token = token['id_token'][:64]

    existing_user = db.find_by_google(id_token)
    if existing_user is not None:
        session_token = gen_session_token(existing_user[0])
        return redirect(url_for('auth_redirect', task='login', userId=existing_user[0], token=session_token.hex()))

    resp = google.get('userinfo')
    user_info = resp.json()
    session['third_party'] = 'google'
    session['user'] = user_info
    email = user_info['email']

    existing_user = db.find_by_email(email)
    if existing_user is not None:
        db.update_google(existing_user[0], id_token)
        session_token = gen_session_token(existing_user[0])
        return redirect(url_for('auth_redirect', task='login', userId=existing_user[0], token=session_token.hex()))

    return redirect(
        url_for('auth_redirect', task='register', thirdParty='Google', name=user_info['name'], email=email, token=id_token))

def user_from_github(github_token):
    gh_user = jsonify(github.get("/user"))
    if gh_user is not None:
        user_data = gh_user.json

        user = db.find_by_github(github_token)
        if user is not None:
            return user, user_data

        if user_data['email'] is not None:
            user = db.find_by_email(user_data['email'])
            print(user)
            if user is not None:
                return user, user_data
            else:
                return None, user_data

@app.route('/login/github')
def github_auth():
    return github.authorize(scope='user')

@app.route('/auth/github')
@github.authorized_handler
def github_authorized(oauth_token):
    if oauth_token is None:
        return redirect('login')

    session['github_token'] = oauth_token
    # print(oauth_token)
    user, user_data = user_from_github(oauth_token)

    if user is not None:
        token = gen_session_token(user[0])
        return redirect(url_for('auth_redirect', task='login', userId=user[0], token=token.hex()))

    else:
        name = user_data['name']
        email = user_data['email']

        return redirect(url_for('auth_redirect', task='register', thirdParty='GitHub', name=name, email=email, token=oauth_token))

@github.access_token_getter
def token_getter():
    token = session.get('github_token')
    if token is not None:
        return token
    return None

@app.route('/create_account', methods=['POST'])
@cross_origin()
def register():
    data = request.json
    print(data)
    created_user = db.create_user(data['email'], data['fullname'], data['password'])
    if created_user is not None:
        return Response(f'"token":{gen_session_token(created_user[0])}', status=201, content_type='application/json')
    else:
        return Response(status=302)

@app.route('/registerFromExternal', methods=['POST'])
@cross_origin()
def register_external():
    data = request.json
    print(data)
    created_user = None
    if data['third_party'] == 'GitHub':
        created_user = db.create_with_github(data['email'], data['fullname'], data['password'], data['third_party_token'])
    elif data['third_party'] == 'Google':
        created_user = db.create_with_google(data['email'], data['fullname'], data['password'], data['third_party_token'])

    if created_user is not None:
        token = gen_session_token(created_user[0]).hex()
        return Response(json.dumps({'token': token}), status=201, content_type='application/json')
    else:
        return Response(status=302)

def gen_session_token(user_id):
    token = random.randbytes(32)
    token_expires = datetime.now() + timedelta(minutes=30)
    db.put_token(user_id, token, token_expires)
    return token

@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    data = request.json
    login_result = db.login_user(data['email'], data['password'])
    if login_result['user_id'] is not None:
        token = gen_session_token(login_result['user_id'])
        return {'status':200, 'user_id': login_result['user_id'], 'token': token.hex()}
    else:
        return Response(status=login_result['status'])

@app.route('/logout', methods=['POST'])
@cross_origin()
def logout():
    token = request.headers['Authorization']
    db.delete_token(bytes.fromhex(token))
    return Response(status=200)

@app.route('/account_info', methods=['GET', 'DELETE'])
@cross_origin()
def account():
    if request.method == 'GET':
        token: str = request.headers['Authorization']
        if token is not None:
            user = db.find_by_token(bytes.fromhex(token))
            if user is not None:
                return {'email': user[1], 'fullname': user[2]}
            else:
                return Response(status=404)
        else:
            return Response(status=400)
    elif request.method == 'DELETE':
        pass

@app.route('/change-password', methods=["POST"])
@cross_origin()
def change_password():
    body = request.json
    token = request.headers['Authorization']
    user = db.find_by_token(bytes.fromhex(token))
    if user is not None:
        user_id = user[0]
        current_password = body['current_password']
        new_password = body['new_password']

        result = db.change_password(user_id, current_password, new_password)
        return Response(status=200)
    else:
        return Response(status=401)

@app.route('/login')
def page_login():
    return render_template("login.html")

@app.route('/register')
def page_register():
    return render_template("register.html")

@app.route('/account')
def page_account():
    return render_template("account.html")

@app.route('/auth_redirect')
def auth_redirect():
    return render_template("github_redirect.html")

@app.route('/register_third_party')
def page_register_tp():
    return render_template('register_from_github.html')

@app.route('/')
def home():
    return render_template("home.html")

if __name__ == '__main__':
    app.run(debug=True)
    db.close()