from flask import Blueprint, request, jsonify
from app.models import Answer, Choice, db

answer_bp = Blueprint('answer', __name__, url_prefix='/submit')

CHOICE_RESULT_MAPPING = { 
	1: {"title": "분석적", "desc": "사실과 데이터 중점적으로 검토하는 성향을 띄고 있습니다"}, 
	2: {"title": "공감 지향적", "desc": "주변 상황을 고려하는 성향을 띄고 있습니다."}, 
	3: {"title": "목표 지향적", "desc": "계획적인 성향을 띄고 있습니다."}, 
	4: {"title": "정밀함 추구", "desc": "정확성을 추구합니다."}, 
	5: {"title": "아이디어 중심", "desc": "번뜩이는 아이디어에 집중을 합니다."}, 
	6: {"title": "경험 존중", "desc": "기존의 경험을 중시합니다."}, 
	7: {"title": "체계적인 업무", "desc": "결과에 도달하기까지 효율적으로 운영합니다."}, 
	8: {"title": "새로운 탐색", "desc": "변수에 따른 변화에 적응을 잘하는 성향입니다."}, 
	9: {"title": "성장 지원", "desc": "다른 사람에게 긍정적인 영향을 줌으로 보람을 느낍니다."}, 
	10: {"title": "관계 중심", "desc": "사람들과의 연결을 통해 심리적 안정감을 얻는 성향이 강합니다."}, 
	11: {"title": "자기 관리형", "desc": "내면의 평화를 찾고 자신을 돌아보는 시간에 가치를 둡니다."}, 
	12: {"title": "자유로운", "desc": "즉흥적이고 유연한 방식으로 휴식을 취하며 스트레스를 해소하는 경향을 띕니다."}, 
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