from flask import Blueprint
# 각 모듈에서 Blueprint 가져오기
from .stats_routes import stats_routes_bp
from .users import users_bp
from .questions import questions_bp
from .choices import choice_bp
from .images import images_bp
from .answers import answers_bp

# 모든 Blueprint들을 리스트로 관리 -> 유지보수와 확장성을 위해
blueprints = [
    stats_routes_bp,
    users_bp,
    questions_bp,
    choice_bp,
    images_bp,
    answers_bp
]

# Flask 앱에 모든 Blueprint들을 등록하는 함수
def register_routes(app):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)