from repository import Repository
from mapper import survey_mapper,response_mapper,get_max_id

class SurveyService:
    def __init__(self):
        self.survey_repo = Repository("surveys", survey_mapper)
    ### survey methods ###
    def get_all_surveys(self):
        return self.survey_repo.get_items()
    
    def get_survey(self, survey_id):
        return self.survey_repo.get_by_id(survey_id)

    def add_survey(self, survey_data):
        return self.survey_repo.add(survey_data)
    
    def delete_survey(self, survey_id):
        return self.survey_repo.delete(survey_id)
    
    def update_survey(self, survey_id, updates):
        return self.survey_repo.update(survey_id, updates)
    
    ### question methods ###

    def get_all_questions(self, survey_id):
        survey = self.survey_repo.get_by_id(survey_id)
        return survey.get("questions", [])
    
    def get_question(self, survey_id, question_id):
        survey = self.survey_repo.get_by_id(survey_id)
        for question in survey.get("questions", []):
            if int(question["id"]) == int(question_id):
                return question
        raise LookupError(f"Question with ID {question_id} not found in survey {survey_id}.")
    
    def add_question(self, survey_id, question_data):
        surveys = self.survey_repo.get_items()
        for survey in surveys:
            if int(survey["id"]) == int(survey_id):
                q_id=get_max_id(survey["questions"])
                new_question = {
                    "id": q_id,
                    "text": question_data.get("text"),
                    "type": question_data.get("type", "text"),
                    "options": question_data.get("options", [])
                }
                survey["questions"].append(new_question)
                self.survey_repo.save_db(surveys)
                return new_question
        raise LookupError(f"Survey with ID {survey_id} not found.")
    

    def delete_question(self, survey_id, question_id):
        surveys = self.survey_repo.get_items()
        for survey in surveys:
            if int(survey["id"]) == int(survey_id):
                old_len = len(survey["questions"])
                survey["questions"] = [q for q in survey["questions"] if int(q["id"]) != int(question_id)]
                if len(survey["questions"]) == old_len:
                    raise LookupError(f"Question {question_id} not found in survey {survey_id}.")
                self.survey_repo.save_db(surveys)
                return True
        raise LookupError(f"Survey {survey_id} not found.")
    
    
    def update_question(self, survey_id, question_id, updates):
        surveys = self.survey_repo.get_items()
        for survey in surveys:
            if int(survey["id"]) == int(survey_id):
                for q in survey["questions"]:
                    if int(q["id"]) == int(question_id):
                        q.update(updates)
                        self.survey_repo.save_db(surveys)
                        return q
                raise LookupError(f"Question {question_id} not found in survey {survey_id}.")
        raise LookupError(f"Survey {survey_id} not found.")



class ResponseService:
    def __init__(self, survey_repo):
        self.response_repo = Repository("responses", response_mapper)
        self.survey_repo = survey_repo  

    def get_responses(self, survey_id=None, respondent=None):
        responses = self.response_repo.get_items()
        if survey_id:
            responses = [r for r in responses if int(r["survey_id"]) == int(survey_id)]
        if respondent:
            responses = [r for r in responses if r.get("respondent") == respondent]
        return responses

    def get_response(self, response_id):
        """Return one response by ID"""
        return self.response_repo.get_by_id(response_id)
    
    def delete_response(self, response_id):
        return self.response_repo.delete(response_id)

    def submit_response(self, survey_id, respondent, answers):
        survey = self.survey_repo.get_by_id(survey_id)
        valid_qids = {q["id"] for q in survey["questions"]}
        for a in answers:
            if a["question_id"] not in valid_qids:
                raise ValueError(f"Question ID {a['question_id']} does not exist in survey {survey_id}")
        response_data = {
            "survey_id": survey_id,
            "respondent": respondent,
            "answers": answers
        }
        return self.response_repo.add(response_data)
    
    def get_survey_with_responses(self, survey_id, respondent=None):
        """
        Returns a survey including its questions and responses.
        """
        survey = self.survey_repo.get_by_id(survey_id)
        responses = self.response_service.get_responses(survey_id=survey_id, respondent=respondent)
        full_survey = survey.copy()  
        full_survey["responses"] = responses
        return full_survey

    
