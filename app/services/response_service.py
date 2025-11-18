from app.repository.json_repository import Repository
from app.mappers.response import map_response
from app.mappers.survey import map_survey
from werkzeug.exceptions import NotFound, BadRequest

class ResponseService:
    def __init__(self):
        self.response_repo = Repository("responses", map_response)
        self.survey_repo = Repository("surveys", map_survey)

    def get_responses(self, survey_id=None, respondent=None):
        res = self.response_repo.get_items()
        if survey_id:
            res = [r for r in res if int(r["survey_id"]) == int(survey_id)]
        if respondent:
            res = [r for r in res if r.get("respondent") == respondent]
        return res

    def get_response(self, response_id):
        try:
            return self.response_repo.get_by_id(response_id)
        except Exception:
            raise NotFound("Response not found")

    def delete_response(self, response_id):
        try:
            return self.response_repo.delete(response_id)
        except Exception:
            raise NotFound("Response not found")
        
    def delete_by_survey(self, survey_id):
        all_res = self.response_repo.get_items()
        filtered = [r for r in all_res if int(r["survey_id"]) != int(survey_id)]
        self.response_repo.save_db(filtered)
        return True

    def submit(self, survey_id, respondent, answers):
        survey = self.survey_repo.get_by_id(survey_id)
        if not survey:
            raise NotFound("Survey not found")

        valid_ids = {q["id"] for q in survey["questions"]}

        clean_answers = []
        for ans in answers:
            qid = int(ans.get("question_id", -1))
            if qid not in valid_ids:
                raise ValueError(f"Invalid question ID: {qid}")
            answer_val = ans.get("answer", "")
            clean_answers.append({
                "question_id": qid,
                "answer": str(answer_val)
            })

        response_data = {
            "survey_id": survey_id,
            "respondent": respondent or "anonymous",
            "answers": clean_answers
        }

        return self.response_repo.add(response_data)

    def get_survey_with_responses(self, survey_id, respondent=None):
        survey = self.survey_repo.get_by_id(survey_id)
        responses = self.get_responses(survey_id=survey_id, respondent=respondent)

        full = survey.copy()
        full["responses"] = responses
        return full
