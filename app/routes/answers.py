from flask import Blueprint, request, jsonify
from app.models import Answer, db

answer_bp = Blueprint('answer', __name__, url_prefix='/submit')


# 1. 답변 제출
@answer_bp.route('', methods=['POST'])
def submit_answers():
    data = request.get_json()

    if not isinstance(data, list) or not data:
        return jsonify({'message': 'Invalid data format'}), 400

    for item in data:
        user_id = item.get('user_id')
        choice_id = item.get('choice_id')

        if user_id is None or choice_id is None:
            return jsonify({'message': 'Missing user_id or choice_id'}), 400

        new_answer = Answer(user_id=user_id, choice_id=choice_id)
        db.session.add(new_answer)

    db.session.commit()
    return jsonify({'message': f'User: {data[0]["user_id"]}\'s answers Success Create'}), 201