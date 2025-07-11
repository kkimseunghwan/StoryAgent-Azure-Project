import logging
import os
from openai import AzureOpenAI
from azure.storage.blob import BlobClient

def main(activity_input: dict) -> str:

    file_url = activity_input.get('file_url')
    file_name = activity_input.get('file_name')
    task_id = activity_input.get('task_id')
    
    logging.info(f"음성 파일 처리 시작 [id:{task_id}] {file_url}")

    try:
        # Azure OpenAI 클라이언트
        client = AzureOpenAI(
            azure_endpoint=os.environ["WHISPER_ENDPOIND_URL"],
            api_key=os.environ["WHISPER_API_KEY"],
            api_version="2024-03-01-preview" # API 버전 명시
        )
        
        # Blob Storage에서 오디오 파일 다운로드
        # file_url에서 컨테이너 이름과 blob 이름을 추출
        container_name = file_url.split('/')[4] # request-files 컨테이너
        blob_name = f"{file_name}"
        
        # BlobStorage 클라이언트 생성
        blob_client = BlobClient.from_connection_string(
            conn_str=os.environ["FILE_STORAGE_CONNECTION_STRING"],
            container_name=container_name,
            blob_name=blob_name
        )
        
        # Blob에서 오디오 데이터 다운로드
        audio_data = blob_client.download_blob().readall()

        korean_prompt = "이것은 한국어 오디오에 대한 스크립트입니다. 음성을 텍스트로 변환하여 한국어로 출력해주세요. 출력 맨 마지막 위치에 특수문자 ! 를 붙여주세요"

        # Azure OpenAI Whisper API 호출
        #    - 파일 데이터와 함께 가상의 파일명을 튜플로 전달
        text_script = client.audio.transcriptions.create(
            model="StoryAgent-whisper",
            file=("filename.mp3", audio_data),
            language="ko"
        )
        
        logging.info(f"음성 처리 완료. 결과: {text_script.text}")
        return text_script.text

    except Exception as e:
        logging.error(f"오류 발생: {e}")
        return f"Error: {str(e)}"