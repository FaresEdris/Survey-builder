from app.repository.json_repository import Repository
from app.mappers.survey import  map_survey
from datetime import datetime, timezone

class QuestionService:
    def __init__(self):
        self.survey_repo = Repository("surveys", map_survey)

    def get_all(self, survey_id):
        survey = self.survey_repo.get_by_id(survey_id)
        return survey.get("questions", [])
    
    def get(self, survey_id, q_id):
        survey = self.survey_repo.get_by_id(survey_id)
        for q in survey.get("questions", []):
            if int(q["id"]) == int(q_id):
                return q
        raise LookupError(f"Question {q_id} not found.")

    def add(self, survey_id, q_data):
        surveys = self.survey_repo.get_items()
        for survey in surveys:
            if survey["id"] == survey_id:
                q = {
                    "text": q_data["text"],
                    "type": q_data.get("type", "text"),
                    "options": q_data.get("options", []),
                    "deleted": False
                }
                survey["questions"].append(q)
                survey["updated_at"] = datetime.now(timezone.utc).isoformat()
                self.survey_repo.save_db(surveys)
                return q
        raise LookupError("Survey not found.")

    def delete(self, survey_id, q_id):
        surveys = self.survey_repo.get_items()
        for s in surveys:
            if s["id"] == survey_id:
                before = len(s["questions"])
                s["questions"] = [q for q in s["questions"] if q["id"] != q_id]
                if len(s["questions"]) == before:
                    raise LookupError("Question not found.")
                
                s["updated_at"] = datetime.now(timezone.utc).isoformat()
                self.survey_repo.save_db(surveys)
                return True
        raise LookupError("Survey not found.")

    def update(self, survey_id, q_id, updates):
        surveys = self.survey_repo.get_items()
        for s in surveys:
            if s["id"] == survey_id:
                for q in s["questions"]:
                    if q["id"] == q_id:
                        q.update(updates)
                        s["updated_at"] = datetime.now(timezone.utc).isoformat()
                        self.survey_repo.save_db(surveys)
                        return q
                raise LookupError("Question not found.")
        raise LookupError("Survey not found.")
