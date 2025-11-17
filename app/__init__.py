from flask import Flask, render_template
from flask_login import LoginManager
from app.services.user_service import UserService

def create_app():
    app = Flask(__name__,template_folder='../templates', static_folder='../static')
    app.secret_key = "secret"
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"   # because blueprint = "auth"
    login_manager.init_app(app)
    user_service = UserService()

    @login_manager.user_loader
    def load_user(user_id):
        return user_service.get_user_by_id(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.survey_routes import survey_bp
    from app.routes.control_routes import survey_control_bp

    app.register_blueprint(survey_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(survey_control_bp)
    
    @app.route("/")
    def index():
        return render_template("index.html")

    return app
