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
    
    def _as_list(self, form, key):
        """Return a list for key whether form stores list or single value."""
        v = form.get(key)
        if v is None:
            return []
        return v if isinstance(v, list) else [v]

    def _first(self, form, key, default=""):
        v = form.get(key)
        if v is None:
            return default
        return v[0] if isinstance(v, list) else v

    def update_survey_from_form(self, survey_id, form):
        """
        form: mapping produced by request.form.to_dict(flat=False)
              or your test-like dict with lists.
        """
        surveys = self.survey_repo.get_items()
        survey = next((s for s in surveys if s["id"] == survey_id), None)
        if not survey:
            raise LookupError("Survey not found")

        # Update title/description (support list or single)
        survey["title"] = self._first(form, "title", survey.get("title", "")).strip() or survey["title"]
        survey["description"] = self._first(form, "description", survey.get("description", "")).strip() or survey["description"]

        # Collect question ids (support both repeated 'question_id' and explicit keys)
        qid_list = [int(v) for v in self._as_list(form, "question_id") if str(v).strip()]

        # Build quick lookup for existing questions
        q_by_id = {q["id"]: q for q in survey.get("questions", [])}

        # For each existing question id, read keyed fields first, fall back to arrays
        for idx, qid in enumerate(qid_list):
            q = q_by_id.get(qid)
            if not q:
                continue

            # 1) text: prefer keyed name question_text_<id> else array position
            text_key = f"question_text_{qid}"
            if text_key in form:
                new_text = self._first(form, text_key).strip()
                if new_text:
                    q["text"] = new_text
            else:
                # fallback to array-style by index
                texts = self._as_list(form, "question_text")
                if idx < len(texts):
                    new_text = texts[idx].strip()
                    if new_text:
                        q["text"] = new_text

            # 2) options (multiple-choice): prefer keyed option, else array style
            if q.get("type") == "multiple":
                opt_key = f"question_options_{qid}"
                if opt_key in form:
                    raw = self._first(form, opt_key).strip()
                    if raw != "":
                        q["options"] = [o.strip() for o in raw.split(",") if o.strip()]
                    # if empty string -> treat as "no change" (keeps existing options)
                else:
                    opts_arr = self._as_list(form, "question_options")
                    if idx < len(opts_arr):
                        raw = opts_arr[idx].strip()
                        if raw != "":
                            q["options"] = [o.strip() for o in raw.split(",") if o.strip()]

            # 3) deleted flag: prefer keyed checkbox name, otherwise array-style values
            del_key = f"question_delete_{qid}"
            if del_key in form:
                # checkbox present => checked; value "1" or so
                q["deleted"] = True if self._first(form, del_key) else True
            else:
                # fallback: check array of deletes (values are ids)
                deletes = self._as_list(form, "question_delete")
                q["deleted"] = str(qid) in [str(x) for x in deletes]

        # Handle new questions (array-style)
        new_texts = self._as_list(form, "new_question_text")
        new_types = self._as_list(form, "new_question_type")
        new_opts = self._as_list(form, "new_question_options")

        max_q_id = max((q["id"] for q in survey.get("questions", [])), default=0)
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

        # timestamp
        survey["updated_at"] = datetime.now(timezone.utc).isoformat()

        # persist
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

    
