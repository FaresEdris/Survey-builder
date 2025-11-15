from repository import Repository
from mapper import survey_mapper,response_mapper,get_max_id
from datetime import datetime, timezone

class SurveyService:
    def __init__(self):
        self.survey_repo = Repository("surveys", survey_mapper)
    ### survey methods ###
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
    

    def update_survey_from_form(self, survey_id, form_data):
        surveys = self.survey_repo.get_items()
        survey = next((s for s in surveys if s["id"] == survey_id), None)
        if not survey:
            raise LookupError("Survey not found")

        # ---- Update basic fields ----
        survey["title"] = form_data.get("title", [survey["title"]])[0].strip() or survey["title"]
        survey["description"] = form_data.get("description", [survey["description"]])[0].strip() or survey["description"]

        # ---- Update existing questions ----
        existing_ids = form_data.get("question_id", [])
        texts = form_data.get("question_text", [])
        options_list = form_data.get("question_options", [])
        delete_flags = form_data.get("question_delete", [])

        q_by_id = {q["id"]: q for q in survey["questions"]}

        for idx, qid_str in enumerate(existing_ids):
            try:
                qid = int(qid_str)
            except ValueError:
                continue
            if qid not in q_by_id:
                continue

            q = q_by_id[qid]

            # Update question text
            if idx < len(texts):
                new_text = texts[idx].strip()
                if new_text:
                    q["text"] = new_text

            # Update options only for multiple-choice, if provided
            if q.get("type") == "multiple" and idx < len(options_list):
                raw_opts = options_list[idx].strip()
                if raw_opts:  # only update if user entered something
                    q["options"] = [o.strip() for o in raw_opts.split(",") if o.strip()]

            # Soft delete
            q["deleted"] = str(qid) in delete_flags

        # ---- Add new questions ----
        new_texts = form_data.get("new_question_text", [])
        new_types = form_data.get("new_question_type", [])
        new_opts = form_data.get("new_question_options", [])

        max_q_id = max((q["id"] for q in survey["questions"]), default=0)

        for i, txt in enumerate(new_texts):
            text = txt.strip()
            if not text:
                continue
            qtype = new_types[i] if i < len(new_types) else "text"
            max_q_id += 1
            question = {
                "id": max_q_id,
                "text": text,
                "type": qtype,
                "options": [],
                "deleted": False
            }
            if qtype == "multiple" and i < len(new_opts):
                raw = new_opts[i].strip()
                if raw:
                    question["options"] = [o.strip() for o in raw.split(",") if o.strip()]
            survey["questions"].append(question)

        # ---- Update timestamp ----
        survey["updated_at"] = datetime.now(timezone.utc).isoformat()

        # ---- Persist ----
        self.survey_repo.save_db(surveys)

        return survey

    
    ## new addations

    def get_paginated(self, page=1, per_page=15):
        all_surveys = self.survey_repo.get_items()
        visible_surveys = [s for s in all_surveys if not s["archived"]]
        visible_surveys.sort(key=lambda s: s.get("created_at", ""), reverse=True)
        total = len(visible_surveys)

        start = (page - 1) * per_page
        end = start + per_page

        return {
            "surveys": visible_surveys[start:end],
            "total": total,
            "page": page,
            "has_next": end < total,
            "has_prev": start > 0
        }

    def archive(self, survey_id,user):
        survey = self.survey_repo.get_by_id(survey_id)

        if survey["creator"] != user.username:
            raise PermissionError("You cannot archive surveys you did not create.")

        return self.survey_repo.update(survey_id, {"archived": True})


    def unarchive(self, survey_id,user):
        survey = self.survey_repo.get_by_id(survey_id)

        if survey["creator"] != user.username:
            raise PermissionError("You cannot unarchive surveys you did not create.")
        return self.survey_repo.update(survey_id, {"archived": False})

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
                    "options": question_data.get("options", []),
                    "deleted": False
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
    
        
    def delete_responses_by_survey(self, survey_id):
        responses= self.get_responses()
        responses= [r for r in responses if int(r["survey_id"]) != int(survey_id)]
        self.response_repo.save_db(responses)
        return True

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

    
