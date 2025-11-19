from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.services.survey_service import SurveyService
from app.services.response_service import ResponseService
from werkzeug.exceptions import Forbidden

survey_service = SurveyService()
response_service = ResponseService()

survey_control_bp = Blueprint("survey_control", __name__)


@survey_control_bp.route("/control")
@login_required
def view_all_responses():
    surveys = survey_service.get_all_surveys(username=current_user.username) 
    return render_template("responses_overview.html", surveys=surveys)

@survey_control_bp.route("/surveys/<int:survey_id>/responses/list")
@login_required
def survey_responses_list(survey_id):
    page = request.args.get("page", 1, type=int)
    per_page = 3
    survey = survey_service.get_survey(survey_id, username=current_user.username)
    data = response_service.pageinate_responses(survey_id=survey_id,page=page,per_page=per_page)
    return render_template(
        "survey_responses_list.html",
        survey=survey,
        responses=data["items"],
        page=data["page"],
        total=data["total"],
        pages=data["total_pages"],
        per_page=data["per_page"],
        has_next=data["has_next"],
        has_prev=data["has_prev"]
    )

@survey_control_bp.route("/surveys/<int:survey_id>/edit", methods=["GET", "POST"])
@login_required
def edit_survey(survey_id):
    if request.method == "GET":
        survey = survey_service.get_survey(survey_id, username=current_user.username) 
        return render_template("survey_edit.html", survey=survey)
    survey = survey_service.get_survey(survey_id, username=current_user.username)
    survey_service.update_survey(survey_id, request.json, username=current_user.username)
    return redirect(url_for('survey_control.view_all_responses'))

@survey_control_bp.route("/surveys/<int:survey_id>/delete", methods=["POST"])
@login_required
def delete_survey_route(survey_id):
    survey_service.delete_survey(survey_id, username=current_user.username)
    return redirect(url_for("survey_control.view_all_responses"))

@survey_control_bp.route("/surveys/<int:survey_id>/archive", methods=["POST"])
@login_required
def archive_survey(survey_id):    
    survey_service.archive(survey_id, current_user.username)
    return redirect(url_for("survey.view_surveys"))

@survey_control_bp.route("/surveys/<int:survey_id>/unarchive", methods=["POST"])
@login_required
def unarchive_survey(survey_id):
    survey_service.unarchive(survey_id, current_user.username)
    return redirect(url_for("survey.view_surveys"))


