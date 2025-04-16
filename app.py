from datetime import datetime, timedelta
import bcrypt
import random
import dotenv
from flask import Flask, jsonify, session, render_template, request, Response, url_for
from flask_github import GitHub
from flask_cors import cross_origin
from werkzeug.utils import redirect
from authlib.integrations.flask_client import OAuth

from db_utils import DB

config = dotenv.dotenv_values(".env")
db = DB()
app = Flask(__name__)
app.secret_key = bcrypt.gensalt()
app.config['GITHUB_CLIENT_ID'] = config.get('GITHUB_CLIENT_ID')
app.config['GITHUB_CLIENT_SECRET'] = config.get('GITHUB_CLIENT_SECRET')
github = GitHub(app)

def email_valid(username: str):
    # TODO implement actual checks
    return True

def password_valid(password: str):
    # TODO implement actual checks
    return True

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

@app.route('/github-preauth')
def github_auth():
    return github.authorize(scope='user')

@app.route('/github-auth')
@github.authorized_handler
def github_authorized(oauth_token):
    if oauth_token == None:
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
    created_user = db.create_with_github(data['email'], data['fullname'], data['password'], data['gh_token'])
    if created_user:
        return Response(f'"token":{gen_session_token(created_user[0])}', status=201, content_type='application/json')
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