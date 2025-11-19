from app.mappers.question import map_question
from app.services.survey_service import SurveyService
from werkzeug.exceptions import NotFound, BadRequest

class QuestionService:
    def __init__(self):
        self.survey_service = SurveyService()


    def get_all(self, survey_id):
        survey = self.survey_service.get_survey(survey_id)
        return survey.get("questions", [])
    
    def get(self, survey_id, q_id):
        survey = self.survey_service.get_survey(survey_id)
        for q in survey.get("questions", []):
            if int(q["id"]) == int(q_id):
                return q
        raise NotFound(f"Question {q_id} not found.")

    def add(self,survey_id, question):
        survey= self.survey_service.get_survey(survey_id)
        questions = survey.get("questions", [])
        if questions is None:
            return False
        if question["type"] in ["multiple_choice", "checkbox"]:
            if len(question["options"]) <= 1:
                raise BadRequest("Options are required for multiple choice and checkbox questions.")
        new_question = map_question(question, questions)
        questions.append(new_question)
        self.survey_repo.update(survey_id, {"questions": questions})
        return True

