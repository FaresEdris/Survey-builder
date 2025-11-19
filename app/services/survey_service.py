from flask import jsonify
from app.mappers.question import map_question
from app.repository.json_repository import Repository
from app.mappers.survey import map_survey
from datetime import datetime, timezone
from werkzeug.exceptions import NotFound, BadRequest, Forbidden

class SurveyService:
    def __init__(self):
        self.survey_repo = Repository("surveys", map_survey)

    def get_all_surveys(self, username=None):
        surveys = self.survey_repo.get_items()
        if username:
            surveys = [s for s in surveys if s.get("creator") == username]
        surveys.sort(key=lambda s: s.get("created_at", ""), reverse=True)
        return surveys
    
    def get_survey(self, survey_id,username=None):
        survey = self.survey_repo.get_by_id(survey_id)
        if not survey:
            raise NotFound("Survey not found")
        if username and survey.get("creator") != username:
            raise Forbidden("You are not allowed to access this survey")
        return survey

    def add_survey(self, survey_data):
        title = survey_data.get("title")
        description = survey_data.get("description")
        questions = survey_data.get("questions", [])

        if not title and not description:
            return BadRequest("Title and Description are required")
        if not title:
            return BadRequest("Title is required")
        if not description:
            return BadRequest("Description is required")
        
        return self.survey_repo.add(survey_data)
    
    def delete_survey(self, survey_id):
        survey = self.get_survey(survey_id)
        return self.survey_repo.delete(survey_id)
        

    def paginate_surveys(self, page=1, per_page=15):
        all_surveys = self.get_all_surveys()
        visible = [s for s in all_surveys if not s.get("archived")]
        return self.survey_repo.paginate(visible, page, per_page)
    
    def update_survey(self, survey_id, data,username):
        survey = self.get_survey(survey_id,username=username)
        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
        if not title:
            raise BadRequest("Title cannot be empty")
        if not description:
            raise BadRequest("Description cannot be empty")
        survey["title"],survey["description"] = title, description
        questions_data = data.get("questions", [])
        if not questions_data:
            raise BadRequest("Survey must have at least one question")
        
        updated_questions = []
        for q in questions_data:
            q_id = q.get("id")
            q_text = q.get("text", "").strip()
            q_type = q.get("type", "text")
            q_options = q.get("options", [])
            q_required = bool(q.get("required", False))
            q_deleted = bool(q.get("deleted", False))
            if not q_text:
                raise BadRequest(f"Question text cannot be empty (id={q_id})")
            if q_type in ("multiple", "checkbox") and len(q_options) < 2:
                raise BadRequest(f"Question id={q_id} must have at least 2 options")

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


    def archive(self, survey_id, username):
        survey = self.get_survey(survey_id, username=username)
        return self.survey_repo.update(survey_id, {"archived": True})

    def unarchive(self, survey_id, username):
        survey = self.get_survey(survey_id,username=username)
        return self.survey_repo.update(survey_id, {"archived": False})
