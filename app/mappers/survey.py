from datetime import timezone,datetime

def map_survey(item, data):
    new_id = max([s["id"] for s in data], default=0) + 1

    return {
        "id": new_id,
        "title": item.get("title"),
        "description": item.get("description", ""),
        "questions": [], 
        "creator": item.get("creator"),
        "archived": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": None           
    }