from datetime import datetime, timezone

def map_question(item, existing_questions):
    new_id = max((q["id"] for q in existing_questions), default=0) + 1
    
    q_type = item.get("type", "text")
    if q_type not in ("text", "multiple", "checkbox"):
        q_type = "text"
    
    options = []
    if q_type in ("multiple", "checkbox"):
        raw_options = item.get("options", [])
        if isinstance(raw_options, str):
            # comma-separated string
            options = [o.strip() for o in raw_options.split(",") if o.strip()]
        elif isinstance(raw_options, list):
            options = raw_options

    return {
        "id": new_id,
        "text": item.get("text", "").strip(),
        "type": q_type,
        "options": options,
        "deleted": False,                     
        "required": bool(item.get("required", False)),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": None
    }
