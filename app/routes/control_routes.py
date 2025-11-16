from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.services.survey_service import SurveyService
from app.services.response_service import ResponseService

# initialize services
survey_service = SurveyService()
response_service = ResponseService()

survey_control_bp = Blueprint("survey_control", __name__)

# ----------------------------------------
# Overview of surveys owned by current user
# ----------------------------------------
@survey_control_bp.route("/responses")
@login_required
def view_all_responses():
    surveys = survey_service.get_all_surveys() 
    user_surveys = [s for s in surveys if s.get("creator") == current_user.username]
    return render_template("responses_overview.html", surveys=user_surveys)

# ----------------------------------------
# Survey control page (owner only)
# ----------------------------------------
@survey_control_bp.route("/surveys/<int:survey_id>/responses")
@login_required
def survey_control_page(survey_id):
    survey = survey_service.get_survey(survey_id)
    if not survey: 
        return "Survey not found", 404
    if survey.get("creator") != current_user.username: 
        abort(403)
    # Do NOT load responses here
    return render_template("survey_control.html", survey=survey)

# ----------------------------------------
# Survey responses list for owner
# ----------------------------------------
@survey_control_bp.route("/surveys/<int:survey_id>/responses/list")
@login_required
def survey_responses_list(survey_id):
    survey = survey_service.get_survey(survey_id)
    if not survey: 
        return "Survey not found", 404
    if survey.get("creator") != current_user.username: 
        abort(403)
    responses = response_service.get_responses(survey_id=survey_id)
    return render_template("survey_responses_list.html", survey=survey, responses=responses)

# ----------------------------------------
# Edit survey
# ----------------------------------------
@survey_control_bp.route("/surveys/<int:survey_id>/edit", methods=["GET", "POST"])
@login_required
def edit_survey(survey_id):

    if request.method == "GET":
        survey = survey_service.get_survey(survey_id)
        return render_template("survey_edit.html", survey=survey)

    # POST — apply update
    survey_service.update_survey(survey_id, request.json)
    #survey_service.survey_repo.update(survey_id, request.json)
    flash("Survey updated successfully.")
    return redirect(url_for("survey_control.survey_control_page", survey_id=survey_id))


# ----------------------------------------
# Delete survey
# ----------------------------------------
@survey_control_bp.route("/surveys/<int:survey_id>/delete", methods=["POST"])
@login_required
def delete_survey_route(survey_id):
    survey = survey_service.get_survey(survey_id)
    if not survey: 
        return "Survey not found", 404
    if survey.get("creator") != current_user.username: 
        abort(403)

    try:
        survey_service.survey_repo.delete(survey_id)
    except Exception as e:
        flash("Failed to delete survey: " + str(e))
        return redirect(url_for("survey_control.survey_control_page", survey_id=survey_id))

    try:
        response_service.delete_responses_by_survey(survey_id)
    except Exception:
        pass

    flash("Survey and its responses deleted.")
    return redirect(url_for("survey_control.view_all_responses"))

# ----------------------------------------
# Archive / Unarchive
# ----------------------------------------
@survey_control_bp.route("/surveys/<int:survey_id>/archive", methods=["POST"])
@login_required
def archive_survey(survey_id):
    try:
        survey_service.archive(survey_id, current_user)
        flash("Survey archived.")
    except PermissionError:
        flash("Not allowed.")
    return redirect(url_for("survey.view_surveys"))

@survey_control_bp.route("/surveys/<int:survey_id>/unarchive", methods=["POST"])
@login_required
def unarchive_survey(survey_id):
    try:
        survey_service.unarchive(survey_id, current_user)
        flash("Survey restored.")
    except PermissionError:
        flash("Not allowed.")
    return redirect(url_for("survey.view_surveys"))
