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
