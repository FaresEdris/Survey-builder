from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.services.survey_service import SurveyService
from app.services.response_service import ResponseService
from app.services.question_service import QuestionService

# Initialize services
survey_service = SurveyService()
response_service = ResponseService()
question_service = QuestionService()

survey_bp = Blueprint("survey", __name__)

# ----------- Web routes -----------
@survey_bp.route("/surveys/view")
def view_surveys():
    page = int(request.args.get("page", 1))
    data = survey_service.get_paginated(page=page)
    return render_template("surveys.html", **data)

@survey_bp.route("/surveys/<int:survey_id>/view")
def view_survey_detail(survey_id):
    survey = survey_service.get_survey(survey_id)
    return render_template("survey_detail.html", survey=survey)

@survey_bp.route("/surveys/create")
@login_required
def view_create_survey():
    return render_template("create_survey.html")

# ----------- API routes -----------
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
    title = data.get("title")
    description = data.get("description")
    questions = data.get("questions", [])
    user_name = current_user.username

    survey_data = {
        "title": title,
        "description": description,
        "questions": [],
        "creator": user_name
    }

    # Validation
    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not description:
        return jsonify({"error": "Description is required"}), 400
    if not questions:
        return jsonify({"error": "At least one question is required"}), 400

    new_survey = survey_service.add_survey(survey_data)

    for q in questions:
        question_service.add(new_survey["id"], q)

    return jsonify({"message": "Survey created successfully", "survey": new_survey}), 201

@survey_bp.route("/api/surveys/<int:survey_id>/responses", methods=["POST"])
def api_submit_response(survey_id):
    data = request.json
    respondent = data.get("respondent", "anonymous")
    answers = data.get("answers", [])
    response = response_service.submit(survey_id, respondent, answers)
    return jsonify(response), 201
