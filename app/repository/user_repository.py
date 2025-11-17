from app.repository.json_repository import Repository
from app.mappers.user import map_user
from app.models.user import User

class UserRepository(Repository):
    def __init__(self):
        super().__init__("users", map_user)

    def find_by_username(self, username):
        for item in self.get_items():
            if item["username"] == username:
                return User(item["id"], item["username"], item["password"])
        return None

    def get_user_by_id(self, user_id):
        item = self.get_by_id(user_id)
        return User(item["id"], item["username"], item["password"])

    def add_user(self, username, password):
        user_dict = self.add({"username": username, "password": password})
        return User(user_dict["id"], user_dict["username"], user_dict["password"])
