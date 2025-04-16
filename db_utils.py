import mysql.connector
import dotenv
import bcrypt

from db_queries import *

TABLES = {}

TABLES['site_users'] = create_site_users

class DB:

    @staticmethod
    def check_password(user_data, password):
        hashed = bcrypt.hashpw(password.encode(), user_data[4])
        return hashed == user_data[3]

    def __init__(self, config_path: str = ".env"):
        config = dotenv.dotenv_values(config_path)
        self.conn = mysql.connector.connect(
            host=config.get("DB_HOST"),
            user=config.get("DB_USER"),
            password=config.get("DB_PASS"),
            database=config.get("DB_NAME")
        )
        self.cursor = self.conn.cursor(buffered=True)
        try:
            self.cursor.execute(TABLES['site_users'])
            print("Created new instance of 'site_users' table")
        except mysql.connector.errors.ProgrammingError as e:
            print(e)

    def find_by_x(self, query, value):
        self.cursor.execute(query, [value])
        records = [record for record in self.cursor]
        if len(records) > 0:
            return records[0]
        else:
            return None

    def find_by_email(self, email: str):
        return self.find_by_x(q_get_user_by_email, email)

    def find_by_id(self, user_id):
        return self.find_by_x(q_get_user_by_id, user_id)

    def find_by_token(self, token: bytes):
        return self.find_by_x(q_get_user_by_token, token)

    def find_by_github(self, token: str):
        return self.find_by_x(q_get_user_by_github, token)

    def put_token(self, user_id, token, expire_time):
        self.cursor.execute(q_put_token, (token, expire_time, user_id))
        self.conn.commit()

    def delete_token(self, token):
        self.cursor.execute(q_del_token, [token])
        self.conn.commit()

    def user_exists(self, email):
        return self.find_by_email(email) is not None

    def create_user(self, email: str, fullname: str, password: str):

        if self.user_exists(email):
            return None

        else:
            salt = bcrypt.gensalt()
            passhash = bcrypt.hashpw(password.encode(), salt)
            params = (email, fullname, passhash, salt)
            self.cursor.execute(add_user, params)
            self.conn.commit()

            return self.find_by_email(email)

    def create_with_github(self, email: str, fullname: str, password: str, github_token: str):

        if self.user_exists(email):
            return None

        else:
            salt = bcrypt.gensalt()
            passhash = bcrypt.hashpw(password.encode(), salt)
            params = (email, fullname, passhash, salt, github_token)
            self.cursor.execute(add_from_github, params)
            self.conn.commit()

            return self.find_by_github(github_token)

    def login_user(self, email: str, password: str):
        account = self.find_by_email(email)
        if account is None:
            return {'status': 404, 'user_id': None}
        else:
            if self.check_password(account, password):
                return {'status': 200, 'user_id': account[0]}
            else:
                return {'status': 401, 'user_id': None}

    def change_password(self, user_id, current_password: str, new_password: str):
        user = self.find_by_id(user_id)
        if user is not None:
            user_salt = user[4]
            current_hash = bcrypt.hashpw(current_password.encode(), user_salt)
            new_hash = bcrypt.hashpw(new_password.encode(), user_salt)
            q_result = self.cursor.execute(q_update_password, (new_hash, user_id, current_hash))
            print(q_result)
            self.conn.commit()
            print(c for c in self.cursor)

    def close(self):
        self.cursor.close()
        self.conn.close()
