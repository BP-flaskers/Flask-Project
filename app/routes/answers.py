from flask import Blueprint, request, jsonify
from app.models import Answer, Choice, db

answer_bp = Blueprint('answer', __name__, url_prefix='/submit')

CHOICE_RESULT_MAPPING = {
    1: {"title": "결과1-1", "desc": "설명1"},
    2: {"title": "결과1-2", "desc": "설명2"},
    3: {"title": "결과1-3", "desc": "설명3"},
    4: {"title": "결과2-1", "desc": "설명4"},
    5: {"title": "결과2-2", "desc": "설명5"},
    6: {"title": "결과2-3", "desc": "설명6"},
    7: {"title": "결과3-1", "desc": "설명7"},
    8: {"title": "결과3-2", "desc": "설명8"},
    9: {"title": "결과3-3", "desc": "설명9"},
    10: {"title": "결과4-1", "desc": "설명10"},
    11: {"title": "결과4-2", "desc": "설명11"},
    12: {"title": "결과4-3", "desc": "설명12"},
}

NUM_QUESTIONS = 4

def validate_input(data):
    if not isinstance(data, list) or not data:
        return False, 'Invalid data format, expected non-empty list'
    user_ids = {item.get('user_id') for item in data if 'user_id' in item}
    if len(user_ids) != 1:
        return False, 'All entries must have the same user_id'
    if any('choice_id' not in item for item in data):
        return False, 'Each item must include choice_id'
    return True, user_ids.pop()

@answer_bp.route('', methods=['POST'])
def submit_answers():
    data = request.get_json()

    valid, result = validate_input(data)
    if not valid:
        return jsonify({'message': result}), 400
    user_id = result

    for item in data:
        db.session.add(Answer(user_id=user_id, choice_id=item['choice_id']))

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Database error while saving answers: {e}'}), 500

    # 최신 답변부터 조회
    answers = Answer.query.filter_by(user_id=user_id).order_by(Answer.created_at.desc()).all()
    if len(answers) < NUM_QUESTIONS:
        return jsonify({'message': f'User: {user_id}\'s answers saved, but less than {NUM_QUESTIONS} answers submitted'}), 201

    choice_ids = [a.choice_id for a in answers]
    choices = Choice.query.filter(Choice.id.in_(choice_ids)).all()
    choice_map = {choice.id: choice for choice in choices}

    latest_per_question = {}
    for ans in answers:
        choice = choice_map.get(ans.choice_id)
        if not choice:
            continue
        qid = choice.question_id
        # 최신 답변 덮어쓰기: 가장 최신 답변 유지
        latest_per_question[qid] = ans.choice_id
        if len(latest_per_question) == NUM_QUESTIONS:
            break

    if len(latest_per_question) < NUM_QUESTIONS:
        return jsonify({'message': 'Not enough distinct question answers submitted'}), 201

    sorted_choice_ids = [latest_per_question[q] for q in sorted(latest_per_question.keys())]
    results = [CHOICE_RESULT_MAPPING.get(cid, {"title": "알 수 없음", "desc": ""}) for cid in sorted_choice_ids]

    final_result = (
        f"당신의 심리는 {results[0]['title']}하고 {results[1]['title']}한 상태입니다."
        f"그리고 {results[2]['title']}한 성향과 {results[3]['title']}의 적성을 지닌 사람입니다."
    )

    return jsonify({
        'message': f'User: {user_id}\'s answers Success Create',
        'final_result': final_result,
        'details': results
    }), 201