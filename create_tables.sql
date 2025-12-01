-- PostgreSQL용: UUID 생성 확장 기능 확인 (PostgreSQL 버전 13+에서는 gen_random_uuid() 사용)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. 사용자 정보 테이블
CREATE TABLE IF NOT EXISTS user_info (
    uid VARCHAR(255) PRIMARY KEY,                    -- 구글 ID 기반 고유 ID
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- BM 구조 (횟수 제한)
    paid_tier BOOLEAN DEFAULT FALSE,
    daily_count_4cut INTEGER DEFAULT 0,              -- 일일 4컷 생성 횟수
    daily_count_24s_video INTEGER DEFAULT 0,         -- 일일 24초 영상 생성 횟수
    
    status VARCHAR(50) DEFAULT 'ACTIVE'
);

-- 2. 일일 트렌드 데이터 업데이트 테이블
CREATE TABLE IF NOT EXISTS trend_daily_update (
    trend_id SERIAL PRIMARY KEY,
    date DATE NOT NULL DEFAULT CURRENT_DATE,         -- 업데이트 일자
    outfit_name VARCHAR(255) NOT NULL,
    keywords TEXT,                                   -- AI 프롬프트 생성용
    scraped_url VARCHAR(1024),
    image_url_source VARCHAR(1024),
    is_active BOOLEAN DEFAULT TRUE
);

-- 3. 영상 결과물 및 히스토리 관리 테이블 (Vrew 유사 기능 핵심)
CREATE TABLE IF NOT EXISTS video_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(), -- 결과물 고유 UUID
    uid VARCHAR(255) REFERENCES user_info(uid) ON DELETE CASCADE,
    trend_id INTEGER REFERENCES trend_daily_update(trend_id) ON DELETE SET NULL,
    
    -- 파일 경로
    img_4cut_path VARCHAR(1024),
    video_8s_path VARCHAR(1024),
    video_24s_path VARCHAR(1024),
    
    -- 관리 기능 필드
    prompt_used TEXT,                                  -- 재생성 기능에 사용
    visibility_option VARCHAR(50) DEFAULT 'PRIVATE',   -- 공개 범위 (PRIVATE, LINK_ONLY, PUBLIC)
    status VARCHAR(50) DEFAULT 'COMPLETED',            -- 상태 (COMPLETED, IN_EDIT, DELETED)
    
    generation_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP WITH TIME ZONE             -- Corrected
);
