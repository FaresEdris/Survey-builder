from app.mappers.question import map_question
from app.repository.json_repository import Repository
from app.mappers.survey import map_survey
from datetime import datetime, timezone

class SurveyService:
    def __init__(self):
        self.survey_repo = Repository("surveys", map_survey)

    def get_all_surveys(self):
        surveys = self.survey_repo.get_items()
        surveys.sort(key=lambda s: s.get("created_at", ""), reverse=True)
        return surveys
    
    def get_survey(self, survey_id):
        return self.survey_repo.get_by_id(survey_id)

    def add_survey(self, survey_data):
        return self.survey_repo.add(survey_data)
    
    def delete_survey(self, survey_id):
        return self.survey_repo.delete(survey_id)
    
    def update_metadata(self, survey_id, updates):
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        return self.survey_repo.update(survey_id, updates)

    def get_paginated(self, page=1, per_page=15):
        all_surveys = self.survey_repo.get_items()
        visible = [s for s in all_surveys if not s.get("archived")]
        visible.sort(key=lambda s: s.get("created_at", ""), reverse=True)

        total = len(visible)
        start = (page - 1) * per_page

        return {
            "surveys": visible[start:start+per_page],
            "total": total,
            "page": page,
            "has_next": start + per_page < total,
            "has_prev": start > 0
        }
    
    def update_survey(self, survey_id, data):
        survey = self.survey_repo.get_by_id(survey_id)
        if not survey:
            raise LookupError("Survey not found")

        # Validate title & description
        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
        if not title:
            raise ValueError("Title cannot be empty")
        if not description:
            raise ValueError("Description cannot be empty")

        survey["title"] = title
        survey["description"] = description

        # Questions handling
        questions_data = data.get("questions", [])
        if not questions_data:
            raise ValueError("Survey must have at least one question")

        updated_questions = []
        for q in questions_data:
            q_id = q.get("id")
            q_text = q.get("text", "").strip()
            q_type = q.get("type", "text")
            q_options = q.get("options", [])
            q_required = bool(q.get("required", False))
            q_deleted = bool(q.get("deleted", False))

            # Validation
            if not q_text:
                raise ValueError(f"Question text cannot be empty (id={q_id})")
            if q_type in ("multiple", "checkbox") and len(q_options) < 2:
                raise ValueError(f"Question id={q_id} must have at least 2 options")

            # Keep existing created_at or id
            existing_q = next((ex for ex in survey.get("questions", []) if ex["id"] == q_id), None)
            if existing_q:
                created_at = existing_q.get("created_at")
            else:
                created_at = datetime.now(timezone.utc).isoformat()
                q_id = max((q["id"] for q in survey.get("questions", [])), default=0) + 1

            updated_questions.append({
                "id": q_id,
                "text": q_text,
                "type": q_type,
                "options": q_options,
                "deleted": q_deleted,
                "required": q_required,
                "created_at": created_at,
                "updated_at": datetime.now(timezone.utc).isoformat()
            })

        survey["questions"] = updated_questions
        survey["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.survey_repo.update(survey_id, survey)
        return survey


    def archive(self, survey_id, user):
        survey = self.get_survey(survey_id)
        if survey["creator"] != user.username:
            raise PermissionError("Not allowed.")
        return self.survey_repo.update(survey_id, {"archived": True})

    def unarchive(self, survey_id, user):
        survey = self.get_survey(survey_id)
        if survey["creator"] != user.username:
            raise PermissionError("Not allowed.")
        return self.survey_repo.update(survey_id, {"archived": False})
