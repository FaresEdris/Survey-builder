from werkzeug.security import generate_password_hash

def map_user(item: dict, existing_items: list):
    new_id = max((i["id"] for i in existing_items), default=0) + 1
    return {
        "id": new_id,
        "username": item["username"],
        "password": generate_password_hash(item["password"])
    }