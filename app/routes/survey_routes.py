from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.services.survey_service import SurveyService
from app.services.response_service import ResponseService
from app.services.question_service import QuestionService

survey_service = SurveyService()
response_service = ResponseService()
question_service = QuestionService()

survey_bp = Blueprint("survey", __name__)

@survey_bp.route("/surveys/view")
def view_surveys():
    page = request.args.get("page", 1, type=int)
    data = survey_service.paginate_surveys(page=page, per_page=3)
    return render_template(
        "surveys.html",
        surveys=data["items"],
        page=data["page"],
        total=data["total"],
        pages=data["total_pages"],
        per_page=data["per_page"],
        has_next=data["has_next"],
        has_prev=data["has_prev"]
    )

@survey_bp.route("/surveys/<int:survey_id>/view")
def view_survey_detail(survey_id):
    survey = survey_service.get_survey(survey_id)
    return render_template("survey_detail.html", survey=survey)

@survey_bp.route("/surveys/create")
@login_required
def view_create_survey():
    return render_template("create_survey.html")

# ----------- Json API  -----------
@survey_bp.route("/api/surveys", methods=["GET"])
def api_get_surveys():
    return jsonify(survey_service.get_all_surveys()), 200

@survey_bp.route("/api/surveys/<int:survey_id>", methods=["GET"])
def api_get_survey(survey_id):
    return jsonify(survey_service.get_survey(survey_id)), 200

@survey_bp.route("/api/surveys", methods=["POST"])
@login_required
def create_survey():
    data = request.get_json()
    user_name = current_user.username
    data["creator"] = user_name
    new_survey = survey_service.add_survey(data)
    questions = data.get("questions", [])
    for q in questions:
        valid=question_service.add(new_survey["id"], q)
        if not valid:
            return jsonify({"message": "Failed to add question", "question": q}), 400

    return jsonify({"message": "Survey created successfully", "survey": new_survey}), 201

@survey_bp.route("/api/surveys/<int:survey_id>/responses", methods=["POST"])
def api_submit_response(survey_id):
    data = request.json
    respondent = current_user.username if current_user.is_authenticated else "Anonymous"
    answers = data.get("answers", [])
    response = response_service.submit(survey_id, respondent, answers)
    return jsonify(response), 201
