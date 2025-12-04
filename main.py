import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests

# .env 파일에서 환경 변수 로드
load_dotenv()

app = Flask(__name__)
# 모든 출처에서의 요청을 허용 (개발 목적으로, 실제 서비스에서는 특정 출처만 허용하도록 변경 권장)
CORS(app)

# Gemini API 키를 환경 변수에서 가져옵니다.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

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

        # Gemini API 요청 페이로드 구성
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt_text},
                    {"inlineData": {"mimeType": image_mime_type, "data": image_data}}
                ]
            }],
            "generationConfig": {"responseMimeType": "image/jpeg"} # 이미지 응답을 명시적으로 요청
        }

        # Gemini API 호출
        headers = {
            "Content-Type": "application/json"
        }
        # API 키를 쿼리 파라미터로 추가
        gemini_response = requests.post(
            f"{GEMINI_API_BASE_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload
        )
        gemini_response.raise_for_status() # HTTP 오류가 발생하면 예외 발생

        gemini_data = gemini_response.json()

        # Gemini API 응답에서 이미지 데이터 추출
        # 응답 구조에 따라 추출 로직을 조정해야 할 수 있습니다.
        # 예: gemini_data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
        result_image_base64 = None
        if "candidates" in gemini_data and len(gemini_data["candidates"]) > 0:
            for part in gemini_data["candidates"][0]["content"]["parts"]:
                if "inlineData" in part and "data" in part["inlineData"]:
                    result_image_base64 = part["inlineData"]["data"]
                    break

        if result_image_base64:
            return jsonify({"image": result_image_base64}), 200
        else:
            return jsonify({"error": "No image data found in Gemini API response", "gemini_response": gemini_data}), 500

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 500
    except requests.exceptions.RequestException as re:
        return jsonify({"error": f"Failed to connect to Gemini API: {str(re)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # Flask 서버 실행. 개발 모드에서는 디버그를 True로 설정할 수 있습니다.
    # host='0.0.0.0'으로 설정하면 외부에서도 접근 가능합니다.
    app.run(debug=True, host='127.0.0.1', port=5000)