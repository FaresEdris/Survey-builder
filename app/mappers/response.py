from datetime import timezone,datetime


def map_response(item, data):
    new_id = max([s["id"] for s in data], default=0) + 1

    return {
        "id": new_id,
        "survey_id": item.get("survey_id"),
        "respondent": item.get("respondent", "anonymous"),
        "answers": item.get("answers", []),
        "submitted_at": datetime.now(timezone.utc).isoformat()
    }