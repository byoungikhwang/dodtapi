import subprocess
import json
import os

# FFmpeg 경로 설정 (n8n Docker 환경에 맞게 설정해야 함)
FFMPEG_BIN = "/usr/bin/ffmpeg" 

def create_24s_short_form_video(input_video_8s_path: str, output_path: str, script_json: str):
    """
    8초 원본 영상과 Gemini가 생성한 스크립트 JSON을 기반으로 
    FFmpeg를 사용하여 24초 숏폼 영상을 제작합니다.
    
    프로젝트 기획: 8초 원본을 기반으로 숏폼 트렌드에 최적화된 최종 배포용 영상(24초) 제작.
    """
    
    try:
        script = json.loads(script_json)
        
        # 1. 8초 원본을 24초로 확장하는 편집 규칙 정의 (예: 컷 분할, 루프, 속도 조절 등)
        # 예시: 8초 원본을 3번 반복하고, 사이에 트렌디한 컷 전환 효과를 삽입합니다.
        
        # 2. 자막 삽입 및 배경 음악 (BGM) 적용
        # script['scene_details']에서 자막 텍스트와 타이밍을 추출하여 FFmpeg 필터(drawtext)에 적용합니다.
        # BGM 파일 경로와 오디오 믹싱 로직도 추가해야 합니다.
        
        # 3. FFmpeg 명령어 구성
        # -i: 입력 파일
        # filter_complex: 복잡한 비디오/오디오 필터 체인 (컷 편집, 자막, BGM 믹싱)
        # -t 24: 최종 영상 길이 24초
        
        ffmpeg_command = [
            FFMPEG_BIN,
            "-i", input_video_8s_path,
            # 예시: 8초 영상을 3배속으로 늘이고, 자막과 워터마크를 삽입하는 복잡한 필터 체인이 여기에 들어갑니다.
            "-filter_complex", "[0:v]loop=loop=2:size=1:start=0[looped];[looped]drawtext=text='오늘 무엇을 입을까?':fontsize=30:x=100:y=H-50:fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2",
            "-t", "24", # 24초 길이로 제한
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            output_path,
            "-y" # 덮어쓰기 허용
        ]
        
        # 4. FFmpeg 실행
        subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        
        print(f"24초 숏폼 영상 제작 완료: {output_path}")
        return output_path
        
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg 오류 발생: {e.stderr}")
        raise
    except Exception as e:
        print(f"영상 제작 중 오류 발생: {str(e)}")
        raise

# if __name__ == "__main__":
#     # 테스트를 위한 더미 파일 및 스크립트 설정
#     dummy_input = "/path/to/your/8s_source.mp4" # 8초 원본 파일 경로
#     dummy_output = "/tmp/final_24s_shortform.mp4"
#     dummy_script = json.dumps({
#         "title": "버블 헴 드레스 숏폼 트렌드 리포트",
#         "scene_details": [...] 
#     })
#     # create_24s_short_form_video(dummy_input, dummy_output, dummy_script)