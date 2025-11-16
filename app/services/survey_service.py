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
    
    def update_survey(self, survey_id, form):
        survey = self.survey_repo.get_by_id(survey_id)
        if not survey:
            raise LookupError("Survey not found")
        title = form.get("title")
        description = form.get("description")
        if title is not None:
            survey["title"] = title.strip()
        if description is not None:
            survey["description"] = description.strip()

        for q in survey["questions"]:
            qid = str(q["id"])
            t = form.get(f"text_{qid}")
            if t is not None:
                q["text"] = t.strip()
                q["updated_at"] = datetime.now(timezone.utc).isoformat()
            req = form.get(f"required_{qid}")
            q["required"] = (req == "on")
            del_flag = form.get(f"delete_{qid}")
            q["deleted"] = (del_flag == "on")
            opt_raw = form.get(f"options_{qid}")
            if opt_raw is not None and q["type"] in ("multiple", "checkbox"):
                opt_list = [o.strip() for o in opt_raw.split(",") if o.strip()]
                q["options"] = opt_list
                q["updated_at"] = datetime.now(timezone.utc).isoformat()
        new_q_texts = form.getlist("new_text")
        new_q_types = form.getlist("new_type")
        new_q_options = form.getlist("new_options")
        for text, qtype, ops in zip(new_q_texts, new_q_types, new_q_options):
            if text.strip() == "":
                continue
            new_q_data = {
                "text": text,
                "type": qtype,
                "options": ops,
                "required": False,
            }
            full = map_question(new_q_data, survey["questions"])
            survey["questions"].append(full)
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
