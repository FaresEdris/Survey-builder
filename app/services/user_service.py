from app.repository.user_repository import UserRepository

class UserService:
    def __init__(self):
        self.user_repo = UserRepository()

    def get_user_by_id(self, user_id):
        return self.user_repo.get_user_by_id(user_id)

    def find_by_username(self, username):
        return self.user_repo.find_by_username(username)

    def add_user(self, username, password):
        return self.user_repo.add_user(username, password)
