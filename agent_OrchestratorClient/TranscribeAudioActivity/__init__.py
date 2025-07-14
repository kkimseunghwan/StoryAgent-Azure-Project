import logging
import os
from openai import AzureOpenAI, OpenAI
from azure.storage.blob import BlobClient

def main(activity_input: dict) -> str:

    file_url = activity_input.get('file_url')
    file_name = activity_input.get('file_name')
    task_id = activity_input.get('task_id')
    
    logging.info(f"음성 파일 처리 시작 [id:{task_id}] {file_url}")

    try:
        # Blob Storage에서 오디오 파일 다운로드
        # file_url에서 컨테이너 이름과 blob 이름을 추출
        container_name = "request-files" # request-files 컨테이너
        
        # BlobStorage 클라이언트 생성
        blob_client = BlobClient.from_connection_string(
            conn_str=os.environ["FILE_STORAGE_CONNECTION_STRING"],
            container_name=container_name,
            blob_name=f"{task_id}/{file_name}"
        )
        
        # Blob에서 오디오 데이터 다운로드
        audio_data = blob_client.download_blob().readall()

        # Azure OpenAI Whisper API 호출
        # TODO: Azure OpenAI Whisper API 현재 한국어 지원이 불안정한 상태로 추가적인 언어 설정이 필요할 수 있음.
        # client = AzureOpenAI(
        #     azure_endpoint=os.environ["WHISPER_ENDPOIND_URL"],
        #     api_key=os.environ["WHISPER_API_KEY"],
        #     api_version="2024-03-01-preview" # API 버전 명시
        # )

        # text_script = client.audio.transcriptions.create(
        #     model="StoryAgent-whisper",
        #     file=("filename.mp3", audio_data),
        #     language="ko"
        # )

        # => 일단은 OpenAI Whisper API로 대체하여 사용
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        text_script = client.audio.transcriptions.create(
            model="gpt-4o-transcribe", 
            file=("filename.mp3", audio_data),
            language="ko"
        )

        logging.info(f"음성 처리 완료. 결과: {text_script.text}")
        return text_script.text

    except Exception as e:
        logging.error(f"오류 발생: {e}")
        return f"Error: {str(e)}"