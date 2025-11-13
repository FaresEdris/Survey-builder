from werkzeug.security import generate_password_hash



def get_max_id(data):
    return max([s["id"] for s in data], default=0) + 1

def survey_mapper(item, data):
    new_id = get_max_id(data)

    return {
        "id": new_id,
        "title": item.get("title"),
        "description": item.get("description", ""),
        "questions": [], 
        "creator": item.get("creator") 
    }

def response_mapper(item, data):
    new_id = get_max_id(data)

    return {
        "id": new_id,
        "survey_id": item.get("survey_id"),
        "respondent": item.get("respondent", "anonymous"),
        "answers": item.get("answers", [])
    }

def user_mapper(item, data):
    new_id = get_max_id(data)

    return {
        "id": new_id,
        "username": item.get("username"),
        "password": generate_password_hash(item.get("password"))  
    }
