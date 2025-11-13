from repository import Repository
from mapper import user_mapper
from flask_login import UserMixin
from werkzeug.security import check_password_hash

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class UserRepository(Repository):
    def __init__(self):
        super().__init__("users", user_mapper)

    def find_by_username(self, username):
        data = self.get_items()
        for item in data:
            if item["username"] == username:
                return User(item["id"], item["username"], item["password"])
        return None

    def add_user(self, username, password):
        return self.add({"username": username, "password": password})

    def get_user_by_id(self, user_id):
        item = self.get_by_id(user_id)
        return User(item["id"], item["username"], item["password"])
