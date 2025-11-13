from flask import Flask, jsonify, request, render_template, url_for, redirect, flash
from service import SurveyService, ResponseService
from user_repository import UserRepository
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user


app = Flask(__name__,template_folder='../templates', static_folder='../static')
app.secret_key = 'secret'
CORS(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

survey_service = SurveyService()
response_service = ResponseService(survey_service.survey_repo)
user_repo=UserRepository()
# ----------------------------
# HTML ROUTES (JINJA PAGES)
# ----------------------------

@login_manager.user_loader
def load_user(user_id):
    return user_repo.get_user_by_id(int(user_id))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/surveys/view")
def view_surveys():
    surveys = survey_service.get_all_surveys()
    return render_template("surveys.html", surveys=surveys)

@app.route("/surveys/<int:survey_id>/view")
def view_survey_detail(survey_id):
    survey = survey_service.get_survey(survey_id)
    return render_template("survey_detail.html", survey=survey)

@app.route("/surveys/create")
@login_required
def view_create_survey():
    return render_template("create_survey.html")

@app.route("/responses")
def view_all_responses():
    surveys = survey_service.get_all_surveys() 
    user_surveys = [s for s in surveys if s.get("creator") == current_user.username]
    return render_template("responses_overview.html", surveys=user_surveys)

@app.route("/surveys/<int:survey_id>/responses")
def view_survey_responses(survey_id):
    survey = survey_service.get_survey(survey_id)
    if not survey:
        return "Survey not found", 404

    responses = response_service.get_responses(survey_id=survey_id)

    return render_template("survey_responses.html", survey=survey, responses=responses)

# login route

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_repo.add_user(username, password)
        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = user_repo.find_by_username(username)

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("index"))
        flash("Invalid username or password.")
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return f"Welcome, {current_user.username}!"

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for("login"))



# ----------------------------
# API ROUTES (JSON ENDPOINTS)
# ----------------------------

@app.route("/api/surveys", methods=["GET"])
def api_get_surveys():
    return jsonify(survey_service.get_all_surveys()), 200

@app.route("/api/surveys/<int:survey_id>", methods=["GET"])
def api_get_survey(survey_id):
    return jsonify(survey_service.get_survey(survey_id)), 200

@app.route("/api/surveys", methods=["POST"])
@login_required
def create_survey():
    data = request.get_json()

    title = data.get("title")
    description = data.get("description")
    questions = data.get("questions", [])
    survey_data = {
            "title": title,
            "description": description,
            "questions": [],
            "creator": current_user.username
        }

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not description:
        return jsonify({"error": "Description is required"}), 400
    if not questions:
        return jsonify({"error": "At least one question is required"}), 400

    new_survey = survey_service.add_survey(survey_data)
    for q in questions:
        survey_service.add_question(new_survey["id"], q)

    return jsonify({"message": "Survey created successfully", "survey": new_survey}), 201

@app.route("/api/surveys/<int:survey_id>/responses", methods=["POST"])
def api_submit_response(survey_id):
    data = request.json
    respondent = data.get("respondent", "anonymous")
    answers = data.get("answers", [])
    response = response_service.submit_response(survey_id, respondent, answers)
    return jsonify(response), 201


@app.route("/surveys/<int:survey_id>", methods=["PUT"])
def update_survey(survey_id):
    updates = request.json
    updated = survey_service.update_survey(survey_id, updates)
    return jsonify(updated), 200

@app.route("/surveys/<int:survey_id>", methods=["DELETE"])
def delete_survey(survey_id):
    survey_service.delete_survey(survey_id)
    return jsonify({"message": "Survey deleted"}), 200

# ----------------------------
# Question routes
# ----------------------------

@app.route("/surveys/<int:survey_id>/questions",methods=["GET"])
def get_questions(survey_id):
    questions = survey_service.get_all_questions(survey_id)
    return jsonify(questions), 200

@app.route("/surveys/<int:survey_id>/questions/<int:question_id>", methods=["GET"])
def get_question(survey_id, question_id):
    question = survey_service.get_question(survey_id, question_id)
    return jsonify(question), 200 

@app.route("/surveys/<int:survey_id>/questions", methods=["POST"])
def add_question(survey_id):
    data = request.json
    question = survey_service.add_question(survey_id, data)
    return jsonify(question), 201

@app.route("/surveys/<int:survey_id>/questions/<int:question_id>", methods=["PUT"])
def update_question(survey_id, question_id):
    updates = request.json
    updated = survey_service.update_question(survey_id, question_id, updates)
    return jsonify(updated), 200

@app.route("/surveys/<int:survey_id>/questions/<int:question_id>", methods=["DELETE"])
def delete_question(survey_id, question_id):
    survey_service.delete_question(survey_id, question_id)
    return jsonify({"message": "Question deleted"}), 200



# ----------------------------
# Response routes
# ----------------------------

@app.route("/surveys/<int:survey_id>/responses", methods=["GET"])
def get_responses(survey_id):
    respondent = request.args.get("respondent")
    responses = response_service.get_responses(survey_id=survey_id)
    return jsonify(responses), 200

@app.route("/responses/<int:response_id>", methods=["GET"])
def get_response(response_id):
    response = response_service.get_response(response_id)
    return jsonify(response), 200


@app.route("/responses/<int:response_id>", methods=["DELETE"])
def delete_response(response_id):
    response_service.delete_response(response_id)
    return jsonify({"message": "Response deleted"}), 200

# ----------------------------
# Full survey + responses
# ----------------------------

@app.route("/surveys/<int:survey_id>/full", methods=["GET"])
def get_full_survey(survey_id):
    respondent = request.args.get("respondent")
    full_survey = survey_service.get_survey_with_responses(survey_id, respondent)
    return jsonify(full_survey), 200

# ----------------------------
# Run the app
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)
