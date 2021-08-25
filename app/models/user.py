from werkzeug.security import generate_password_hash, check_password_hash
import secrets, json
from app import app


class User:
    def __init__(self, user, password, token=None):
        self.user = user
        self.password = password
        self.token= token

    def hash_password(self, password):
        self.password =generate_password_hash(password)
        self.write_data()
     
    def generate_session(self):
        self.token = secrets.token_hex(32)
        self.write_data()
        return self.token

    def check_session(self, token):
        if self.token == token:
            return True

    def delete_session(self):
        self.token= None
        self.write_data()
    
    @classmethod
    def read_data(cls,filename):
         with open(app.config['DB_DIR'] + '/' + filename + '.json','r') as f:
            data = json.load(f)
            user, password, token = data['user'], data['password'], data['token']
            return cls(user, password, token)
        

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def write_data (self):
        data={
            "user" : self.user,
            "password" : self.password,
            "token" : self.token
        }

        with open(app.config['DB_DIR'] + '/' + self.user + '.json','w') as f:
            json.dump(data, f)

