import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests # n8n 웹훅 트리거를 위함
import os
from fastapi.middleware.cors import CORSMiddleware # CORS 미들웨어 임포트

# --- 설정 ---
# n8n Webhook URL 설정 (실제 환경에 맞게 변경해야 함)
# User Request Webhook 노드의 URL (예: http://n8n-host:5678/webhook/user-request)
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://n8n-container:5678/webhook/user-request")
# Gemini 프롬프트 JSON 파일 경로
PROMPT_CONFIG_PATH = "gemini_prompt_config.json"

app = FastAPI(
    title="오늘 무엇을 입을까? - AI 콘텐츠 생성 API",
    description="유저 요청을 받아 Gemini 프롬프트를 빌드하고 n8n 자동화 파이프라인을 트리거합니다."
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5501"],  # 프론트엔드 URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic 모델 정의 ---
class GenerationRequest(BaseModel):
    """유저가 프론트엔드에서 입력하는 요청 데이터 모델"""
    trend_id: str
    user_prompt: str # 유저의 추가적인 스타일 요청 (예: 시크하게 연출해 줘)
    output_type: str # 4컷, 30초, MP4 중 유저가 원하는 최종 결과물 타입
    user_uid: str # 구글 로그인으로 얻은 유저 UID

# --- 로직: 프롬프트 구성 및 n8n 트리거 ---
@app.post("/api/generate-content")
async def generate_content(request_data: GenerationRequest):
    """
    유저의 요청에 따라 Gemini 프롬프트를 구성하고 n8n 파이프라인을 트리거합니다.
    """
    try:
        # 1. DB 또는 스크래핑 모듈에서 트렌드 데이터 가져오기
        # 실제 개발 시, trend_id를 사용하여 DB에서 outfit_name, keywords, image_url 등을 조회해야 함.
        # 이 단계에서 스크래핑/DB 조회가 Python 로직에서 발생합니다.

        # TODO: 여기에 실제 DB 연결 및 쿼리 로직 구현
        # 예:
        # import psycopg2
        # conn = psycopg2.connect(DATABASE_URL)
        # cur = conn.cursor()
        # cur.execute("SELECT outfit_name, keywords, image_url_source FROM trend_daily_update WHERE trend_id = %s", (request_data.trend_id,))
        # trend_data = cur.fetchone()
        # if not trend_data:
        #     raise HTTPException(status_code=404, detail=f"Trend with ID {request_data.trend_id} not found.")
        # scraped_data = {
        #     "outfit_name": trend_data[0],
        #     "keywords": trend_data[1],
        #     "image_url": trend_data[2]
        # }
        # conn.close()

        # Mock 데이터 대신 실제 DB 연동 로직이 들어갈 자리 (현재는 Mock 데이터 반환)
        def get_trend_data_from_db(trend_id: str):
            """
            Placeholder function to simulate fetching trend data from DB.
            In a real application, this would connect to a PostgreSQL database
            and query the 'trend_daily_update' table.
            """
            # For demonstration, returning a mock based on the trend_id
            if trend_id == "1":
                return {
                    "outfit_name": "버블 헴 드레스",
                    "keywords": "#Volume #BubbleHem #Sculptural",
                    "image_url": "http://example.com/bubble-dress.jpg"
                }
            elif trend_id == "2":
                return {
                    "outfit_name": "오버사이즈 블레이저",
                    "keywords": "#Oversized #Tailoring #Androgynous",
                    "image_url": "http://example.com/oversized-blazer.jpg"
                }
            else:
                return {
                    "outfit_name": "알 수 없는 트렌드",
                    "keywords": "#Unknown",
                    "image_url": "http://example.com/default.jpg"
                }

        scraped_data = get_trend_data_from_db(request_data.trend_id)
        
        # 2. Gemini 프롬프트 JSON 파일 로드
        with open(PROMPT_CONFIG_PATH, 'r', encoding='utf-8') as f:
            prompt_config = json.load(f)
            
        # 3. Prompt Builder 로직 (Gemini API 호출을 위한 최종 프롬프트 구성)
        # prompt_config['contents'][0]['parts'][0]['text'] 내의 플레이스홀더를 실제 값으로 대체해야 함.
        # 여기서는 단순 FastAPI → n8n 전달만 하고, 실제 Gemini 호출은 n8n의 LLM 노드에서 한다고 가정합니다.

        # n8n 웹훅으로 전달할 최종 데이터 구조
        payload_to_n8n = {
            "trend_id": request_data.trend_id,
            "user_uid": request_data.user_uid,
            "user_prompt": request_data.user_prompt,
            "output_type": request_data.output_type,
            "scraped_data": scraped_data, # 스크래핑 데이터 포함
            "gemini_prompt_json": prompt_config # Gemini 프롬프트 구조 자체를 n8n에 전달

        # 4. n8n Webhook 트리거
        response = requests.post(N8N_WEBHOOK_URL, json=payload_to_n8n)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"n8n Webhook 호출 실패: {response.text}")

        # 5. 성공 응답
        return {
            "message": "콘텐츠 생성 요청이 n8n 파이프라인으로 전달되었습니다.",
            "status": "Processing",
            "n8n_response": response.json()
        }

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"프롬프트 설정 파일({PROMPT_CONFIG_PATH})을 찾을 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FastAPI 처리 중 오류 발생: {str(e)}")


# --- 관리자 UI (admin.html) 서빙 엔드포인트 ---
@app.get("/admin")
async def get_admin_ui():
    """
    관리자용 HTML 파일을 서빙하는 엔드포인트 (실제 퍼블리싱 시 구현)
    """
    # 실제로는 admin.html 파일을 읽어와 HTML 응답으로 반환해야 합니다.
    admin_html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head><title>관리자 대시보드</title></head>
    <body>
        <h1>오늘 무엇을 입을까? - 관리자 시스템</h1>
        <p>이용자 관리, 통계 모니터링, 프롬프트 최적화 로그 확인 기능이 구현될 예정입니다.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=admin_html_content, status_code=200)

from fastapi.responses import HTMLResponse