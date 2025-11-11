from flask import Flask, jsonify, request
from service import SurveyService, ResponseService
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# Initialize services
survey_service = SurveyService()
response_service = ResponseService(survey_service.survey_repo)

# ----------------------------
# Survey routes
# ----------------------------

@app.route("/surveys", methods=["GET"])
def get_all_surveys():
    surveys = survey_service.get_all_surveys()
    return jsonify(surveys), 200

@app.route("/surveys/<int:survey_id>", methods=["GET"])
def get_survey(survey_id):
    survey = survey_service.get_survey(survey_id)
    return jsonify(survey), 200

@app.route("/surveys", methods=["POST"])
def add_survey():
    data = request.json
    survey = survey_service.add_survey(data)
    for question in data.get("questions", []):
        survey_service.add_question(survey["id"], question)
    return jsonify(survey), 201

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

@app.route("/surveys/<int:survey_id>/responses", methods=["POST"])
def submit_response(survey_id):
    data = request.json
    respondent = data.get("respondent", "anonymous")
    answers = data.get("answers", [])
    response = response_service.submit_response(survey_id, respondent, answers)
    return jsonify(response), 201

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
