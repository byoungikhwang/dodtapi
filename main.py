import json
import os
import uuid
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
from sqlalchemy import create_engine, Column, String, Text, Boolean, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

# --- 환경 변수 및 설정 ---
SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://n8n-container:5678/webhook/user-request")
PROMPT_CONFIG_PATH = "gemini_prompt_config.json"
DATABASE_URL = "sqlite:///./dodtapi.db"

# --- 데이터베이스 설정 ---
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- ORM 모델 정의 ---
class User(Base):
    __tablename__ = "users"  # 테이블 이름 변경
    uid = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    display_name = Column(String)
    created_at = Column(String, default=lambda: datetime.now().isoformat())
    last_login = Column(String)
    paid_tier = Column(Boolean, default=False)
    daily_count_4cut = Column(Integer, default=0)
    daily_count_24s_video = Column(Integer, default=0)
    status = Column(String, default='ACTIVE')

class SocialAccount(Base):
    __tablename__ = "social_accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_uid = Column(String, ForeignKey("users.uid")) # users 테이블의 uid 참조
    provider = Column(String, nullable=False) # 예: 'google', 'naver'
    provider_user_id = Column(String, unique=True, nullable=False)
    created_at = Column(String, default=lambda: datetime.now().isoformat())

# --- DB 테이블 생성 ---
Base.metadata.create_all(bind=engine)

# --- Pydantic 스키마 정의 ---
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class GenerationRequest(BaseModel):
    trend_id: str
    user_prompt: str
    output_type: str
    user_uid: str

# --- 보안 관련 ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- FastAPI 앱 초기화 ---
app = FastAPI(
    title="오늘 무엇을 입을까? - AI 콘텐츠 생성 API",
    description="사용자 인증, 유저 요청 처리, n8n 자동화 파이프라인 트리거 기능을 제공합니다."
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5501", "http://192.168.0.138:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 의존성 ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- CRUD 함수 ---
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        uid=str(uuid.uuid4()),
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- API 엔드포인트 ---

# 인증 API
@app.post("/api/register", summary="회원가입")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, username=user.username):
        raise HTTPException(status_code=400, detail="이미 사용 중인 아이디입니다.")
    if get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    return create_user(db=db, user=user)

@app.post("/api/login", response_model=Token, summary="로그인")
def login(form_data: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 잘못되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    user.last_login = datetime.now().isoformat()
    db.commit()
    return {"access_token": access_token, "token_type": "bearer"}


# 기존 콘텐츠 생성 API
@app.post("/api/generate-content")
async def generate_content(request_data: GenerationRequest):
    try:
        scraped_data_mock = {
            "outfit_name": "버블 헴 드레스",
            "keywords": "#Volume #BubbleHem #Sculptural",
            "image_url": "http://example.com/bubble-dress.jpg"
        }
        with open(PROMPT_CONFIG_PATH, 'r', encoding='utf-8') as f:
            prompt_config = json.load(f)
        
        payload_to_n8n = {
            "trend_id": request_data.trend_id,
            "user_uid": request_data.user_uid,
            "user_prompt": request_data.user_prompt,
            "output_type": request_data.output_type,
            "scraped_data": scraped_data_mock,
            "gemini_prompt_json": prompt_config
        }
        response = requests.post(N8N_WEBHOOK_URL, json=payload_to_n8n)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"n8n Webhook 호출 실패: {response.text}")
        return {
            "message": "콘텐츠 생성 요청이 n8n 파이프라인으로 전달되었습니다.",
            "status": "Processing",
            "n8n_response": response.json()
        }
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"프롬프트 설정 파일({PROMPT_CONFIG_PATH})을 찾을 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FastAPI 처리 중 오류 발생: {str(e)}")

# 관리자 UI
@app.get("/admin", response_class=HTMLResponse)
async def get_admin_ui():
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

@app.get("/")
def read_root():
    return {"message": "AI Fashion Creator API에 오신 것을 환영합니다."}
