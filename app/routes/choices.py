from flask import Blueprint, request, jsonify
from app.models import Choice, db

choice_bp = Blueprint('choice', __name__, url_prefix='/choice')

# 1. 특정 질문(question_id)의 선택지 리스트 조회
@choice_bp.route('/<int:question_id>', methods=['GET'])
def get_choices(question_id):
    choices = Choice.query.filter_by(question_id=question_id).all()
    if not choices:
        return jsonify({'message': 'Choices not found'}), 404
    results = [choice.to_dict() for choice in choices]
    return jsonify(results), 200


# 2. 새 선택지 추가
@choice_bp.route('', methods=['POST'])
def add_choice():
    data = request.get_json()

    content = data.get('content')
    is_active = data.get('is_active', True)
    sqe = data.get('sqe')
    question_id = data.get('question_id')

    if content is None or question_id is None or sqe is None:
        return jsonify({'message': 'Missing required fields'}), 400

    new_choice = Choice(
        content=content,
        is_active=is_active,
        sqe=sqe,
        question_id=question_id
    )
    db.session.add(new_choice)
    db.session.commit()

    return jsonify({
        'message': f'Content: {new_choice.content} choice Success Create',
        'choice_id': new_choice.id
    }), 201


# 3. 선택지 수정
@choice_bp.route('/<int:choice_id>', methods=['PUT', 'PATCH'])
def update_choice(choice_id):
    choice = Choice.query.get(choice_id)
    if not choice:
        return jsonify({'message': 'Choice not found'}), 404

    data = request.get_json()
    choice.content = data.get('content', choice.content)
    choice.is_active = data.get('is_active', choice.is_active)
    choice.sqe = data.get('sqe', choice.sqe)

    db.session.commit()
    return jsonify({
        'message': f'Choice {choice_id} updated successfully',
        'choice': choice.to_dict()
    }), 200


# 4. 선택지 삭제
@choice_bp.route('/<int:choice_id>', methods=['DELETE'])
def delete_choice(choice_id):
    choice = Choice.query.get(choice_id)
    if not choice:
        return jsonify({'message': 'Choice not found'}), 404

    db.session.delete(choice)
    db.session.commit()
    return jsonify({'message': f'Choice {choice_id} deleted'}), 200
