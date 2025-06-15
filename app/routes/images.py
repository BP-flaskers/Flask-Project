from flask import jsonify, request, Blueprint
from app.models import Image, db

# 이미지 관련 API를 관리하는 Blueprint 생성
images_bp = Blueprint("images", __name__)


# [C] 새로운 이미지 생성
@images_bp.route("/image", methods=["POST"])
def create_image():
    try:
        # 클라이언트 요청에서 JSON 데이터 가져오기
        data = request.get_json()

        # Image 객체 생성 후 DB에 저장
        image = Image(
            url=data["url"],  # 이미지 URL
            type=data["type"],  # 이미지 타입(예: "main", "sub" 등)
        )
        db.session.add(image)
        db.session.commit()

        return jsonify({"message": f"ID: {image.id} Image Successfully Created"}), 201

    except KeyError as e:
        # 필수 필드가 누락된 경우 예외 처리
        return jsonify({"message": f"Missing required field: {str(e)}"}), 400


# [R] 'main' 타입의 첫 번째 이미지를 반환
@images_bp.route("/image/main", methods=["GET"])
def get_main_image_route():
    # "main" 타입의 이미지 중 첫 번째 데이터를 가져오기
    image = Image.query.filter_by(type="main").first()

    return jsonify({"image": image.url if image else None}), 200