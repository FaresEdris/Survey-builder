from datetime import datetime, timezone

def map_question(item, existing_questions):
    new_id = max((q["id"] for q in existing_questions), default=0) + 1
    
    q_type = item.get("type", "text")
    if q_type not in ("text", "multiple", "checkbox"):
        q_type = "text"
    
    options = []
    if q_type in ("multiple", "checkbox"):
        options = item.get("options", [])
        if isinstance(options, str):
            # comma-separated string
            options = [o.strip() for o in options.split(",") if o.strip()]
        elif isinstance(options, list):
            options = options

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
