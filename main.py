import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests
import psycopg2

# .env 파일에서 환경 변수 로드
load_dotenv()

app = Flask(__name__)
# 모든 출처에서의 요청을 허용 (개발 목적으로, 실제 서비스에서는 특정 출처만 허용하도록 변경 권장)
CORS(app)

# --- 환경 변수 로드 및 검증 ---
GEMINI_API_KEY = os.getenv("YOAIzaSyCvLevOs3B-NXMDtUNwZhavPBah37XEFm8")
DB_HOST = os.getenv("DB_HOST", "db_postgresql")
DB_NAME = os.getenv("DB_NAME", "main_db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("admin123") # 비밀번호는 필수

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD 환경 변수가 설정되지 않았습니다.")

# Gemini API의 기본 URL
GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent"

@app.route('/api/generate', methods=['POST'])
def generate_content():
    try:
        data = request.json
        if not data or 'prompt' not in data or 'image' not in data:
            return jsonify({"error": "Missing prompt or image data"}), 400

        prompt_text = data['prompt']
        image_data = data['image'] # Base64 encoded image data
        image_mime_type = data.get('mimeType', 'image/jpeg') # 기본값 설정

        # Gemini API 요청 페이로드 구성 (generationConfig 제거)
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt_text},
                    {"inlineData": {"mimeType": image_mime_type, "data": image_data}}
                ]
            }]
        }

        # Gemini API 호출
        headers = { "Content-Type": "application/json" }
        gemini_response = requests.post(
            f"{GEMINI_API_BASE_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload
        )
        gemini_response.raise_for_status() # HTTP 오류가 발생하면 예외 발생

        gemini_data = gemini_response.json()

        # Gemini API 응답에서 이미지 데이터 추출
        result_image_base64 = None
        if "candidates" in gemini_data and len(gemini_data["candidates"]) > 0:
            for part in gemini_data["candidates"][0]["content"]["parts"]:
                if "inlineData" in part and "data" in part["inlineData"]:
                    result_image_base64 = part["inlineData"]["data"]
                    break

        if result_image_base64:
            return jsonify({"image": result_image_base64}), 200
        else:
            return jsonify({"error": "No image data found in Gemini API response", "details": gemini_data}), 500

    except requests.exceptions.RequestException as re:
        # API 요청 관련 오류를 더 상세하게 로깅하거나 사용자에게 전달
        return jsonify({"error": f"API request failed: {str(re)}", "response_text": re.response.text if re.response else "No response"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


# 로그인 처리 API
@app.route("/login/google", methods=['POST'])
def google_login():
    # --- 1. 클라이언트로부터 이메일 수신 ---
    # 클라이언트가 보낸 JSON 본문에서 'email' 필드를 가져옵니다.
    # 만약 데이터가 없거나 'email' 필드가 없으면 400 오류를 반환합니다.
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({"error": "Email is required in the request body"}), 400
    
    email = data['email']

    conn = None
    try:
        # --- 2. 데이터베이스 연결 ---
        # .env 파일에 설정된 환경 변수를 사용하여 PostgreSQL 데이터베이스에 연결합니다.
        # 비밀번호와 같은 민감한 정보가 코드에 직접 노출되지 않아 안전합니다.
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()

        # --- 3. 사용자 존재 여부 확인 ---
        # 수신된 이메일이 'users' 테이블에 이미 존재하는지 확인합니다.
        cur.execute("SELECT * FROM users WHERE email = %s;", (email,))
        user = cur.fetchone()

        # --- 4. 신규 사용자일 경우 데이터베이스에 추가 ---
        if not user:
            # 사용자가 존재하지 않으면, 새로운 사용자로 'users' 테이블에 이메일을 추가합니다.
            # created_at 필드에는 현재 시각을 기록합니다.
            cur.execute("INSERT INTO users (email, created_at) VALUES (%s, NOW());", (email,))
            # 변경사항을 데이터베이스에 최종 반영합니다.
            conn.commit()
            message = "회원가입 및 로그인 성공"
        else:
            message = "로그인 성공"

        # --- 5. 작업 완료 후 연결 종료 및 성공 응답 반환 ---
        cur.close()
        return jsonify({"message": message, "email": email})

    except psycopg2.Error as db_error:
        # --- 오류 처리 (데이터베이스) ---
        # 데이터베이스 연결 또는 쿼리 실행 중 오류가 발생하면 500 오류를 반환합니다.
        return jsonify({"error": f"Database connection or query failed: {db_error}"}), 500
    except Exception as e:
        # --- 오류 처리 (기타) ---
        # 그 외의 예기치 않은 서버 오류 발생 시 500 오류를 반환합니다.
        return jsonify({"error": f"An unexpected server error occurred: {e}"}), 500
    finally:
        # --- 6. 데이터베이스 연결 해제 ---
        # 모든 작업이 끝난 후, 데이터베이스 연결을 반드시 종료하여 리소스를 해제합니다.
        if conn:
            conn.close()


if __name__ == '__main__':
    # Flask 서버 실행.
    # host='0.0.0.0'으로 설정하면 외부에서도 접근 가능합니다.
    app.run(debug=True, host='127.0.0.1', port=5000)
    # http://192.168.0.138:5500/html/index.html