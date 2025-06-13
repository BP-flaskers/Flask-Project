from flask import request, Blueprint, jsonify
from app.models import Question, Image, Choices
from app import db

questions_bp = Blueprint("questions", __name__)

# CREATE
@questions_bp.route("/questions", methods=["POST"])
def create_questions():
    try:
        data = request.get_json()

        # 필드 검증
        required_fields = ["title", "sqe", "image_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"msg":f"Missing field: {field}"}), 400

        # 이미지 유무 확인
        image = Image.query.get(data["image_id"])
        if not image:
            return jsonify({"msg":"Image not found"}), 404

        # 이미지 타입을 검증
        if image.type.value != "sub":
            return jsonify({"msg": "Image type must be 'sub'"}), 400

        question = Question(
            title=data["title"],
            sqe=data["sqe"],
            image_id=data["image_id"],
            is_active=data.get("is_active", True),
        )

        db.session.add(question)
        db.session.commit()
        return jsonify({
            "msg":"Question created",
            "question_id": question.id,
            "sqe": question.sqe
        }), 201

# 질문 ID를 반환하는 API
@questions_bp.route("/questions/<int:question_id>", methods=["GET"])
def get_question(question_sqe):
    try:
        question = Question.query.filter_by(sqe=question_sqe, is_active=True).first()
        if not question:
            return jsonify({"msg": "질문이 존재하지 않습니다."}), 404
        image = Image.query.get(question.image_id)
        choice_list = (
            Choices.query.filter_by(question_id=question_sqe, is_active=True)
            .order_by(Choices.sqe)
            .all()
        )

        return jsonify({
            "question_id": question.id,
            "sqe": question.sqe,
            "title": question.title,
            "image": image.url if image else None,
            "choices": [choice.to_dict() for choice in choice_list],
            "is_active": question.is_active
        }), 200

    except Exception as e:
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500

@questions_bp.route("/questions", methods={"GET"})
def get_all_questions():
    try:
        # 페이지 번호와 한 페이지당 개수 설정
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # 활성화된 질문을 조회
        questions = Question.query.filter_by(is_active=True)\
        .order_by(Question.sqe)\
        .paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            "questions": [
                {
                    "id": q.id,
                    "sqe": q.sqe,
                    "title": q.title,
                    "image_id": q.image_id,
                    "is_active": q.is_active
                } for q in questions.items
            ],
            "total": questions.total,
            "page": questions.page,
            "per_page": questions.per_page,
            "pages": questions.pages
        }), 200

    except Exception as e:
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500 # 서버 요청에 오류가 발생했을 시 발생하는 에러 메세지

@questions_bp.route("/questions/count", methods=["GET"])
def count_question():
    try:
        count = Question.query.filter_by(is_active=True).count()
        return jsonify({"total": count}), 200
    except Exception as e:
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500 # 서버 요청에 오류가 발생했을 시 발생하는 에러 메세지

@questions_bp.route("/questions/<int:question_sqe>", methods=["PUT"])
def update_question(question_sqe):
    try:
        question = Question.query.filter_by(sqe=question_sqe, is_active=True).first()
        if not question:
            return jsonify({"msg": "질문이 존재하지 않습니다."}), 404

        data = request.get_json()

        if "title" in data:
            question.title = data["title"]

        if "image_id" in data:
            image = Image.query.get(data["image_id"])
            if not image:
                return jsonify({"msg": "Image not found"}), 404
            if image.type.value != "sub":
                return jsonify({"msg": "Image type must be 'sub'"}), 400
            question.image_id = data["image_id"]

        if "is_active" in data:
            question.is_active = data["is_active"]

        db.session.commit()

        return jsonify({
            "message": f"Question {question_sqe} updated Successfully",
            "question": {
                "id": question.id,
                "sqe": question.sqe,
                "title": question.title,
                "image_id": question.image_id,
                "is_active": question.is_active
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500

@questions_bp.route("/questions/<int:question_sqe>", methods=["DELETE"])
def delete_question(question_sqe):
    try:
        question = Question.query.filter_by(sqe=question_sqe, is_active=True).first()
        if not question:
            return jsonify({"msg": "질문이 존재하지 않습니다."}), 404

        question.is_active = False

        choices = Choices.query.filter_by(question_id=question_sqe).all()
        for choice in choices:
            choice.is_active = False

        db.session.commit()

        return jsonify({
            "msg": f"Question {question_sqe} deleted Successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500