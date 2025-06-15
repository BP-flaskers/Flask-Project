# users.py
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from app.models import db, User

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET']) # user 페이지
def get_user_page():
    if request.method == 'GET':
        return jsonify({'msg':'연결 완'})

@users_bp.route('/signup', methods=['POST'])
def signup():
    if request.method == "POST":
        try:
            data = request.get_json() # 사용자가 입력한 데이터
            # 데이터 분할 -> DB 저장
            user = User( # user 변수에 저장, 클래스를 통해 객체 저장.
                name=data['name'],
                age=data['age'],
                gender=data['gender'],
                email=data['email']
            )
            db.session.add(user) # DB에 끌어오기.
            db.session.commit() # DB에 업로드

            return jsonify(
                {'message' : f'{user.name}님 회원가입이 완료 되었습니다.'}
            )
        # 에러 처리
        except IntegrityError: 
            db.session.rollback()
            return jsonify({'error': '이미 존재하는 이메일 주소입니다. 다른 이메일을 사용해 주세요.'}), 409 # 409 중복에러 

        except Exception as e: 
            db.session.rollback()
            return jsonify({'error': '회원가입 중 예상치 못한 오류가 발생했습니다.', 'details': str(e)}), 500 # 500 서버에러

    # return jsonify({'msg':'Successfully'})