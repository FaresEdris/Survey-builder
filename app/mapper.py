def get_max_id(data):
    #makes easier to get the next Id
    return max([s["id"] for s in data], default=0) + 1

def survey_mapper(item, data):
    new_id = get_max_id(data)

    return {
        "id": new_id,
        "title": item.get("title"),
        "description": item.get("description", ""),
        "questions": []  
    }


""" def question_mapper(item, data):

    new_id = get_max_id(data)

    return {
        "id": new_id,
        "survey_id": item.get("survey_id"),
        "text": item.get("text"),
        "type": item.get("type", "text"),
        "options": item.get("options", [])
    } """

def response_mapper(item, data):
    new_id = get_max_id(data)

    return {
        "id": new_id,
        "survey_id": item.get("survey_id"),
        "respondent": item.get("respondent", "anonymous"),
        "answers": item.get("answers", [])
    }
