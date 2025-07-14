import logging
import os
from azure.storage.blob import BlobServiceClient

def main(data_to_save: dict) -> str:
    task_id = data_to_save.get("task_id")
    content = data_to_save.get("content")

    logging.info(f"작업 ID {task_id}의 결과를 저장합니다.")
    try:
        # Blob Storage 클라이언트 생성
        blob_service_client = BlobServiceClient.from_connection_string(os.environ["FILE_STORAGE_CONNECTION_STRING"])

        # 결과를 저장할 컨테이너 및 파일명 설정
        container_name = "processed-files"
        blob_name = f"{task_id}/combined_text.txt"

        # 컨테이너 연결
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        # 텍스트 내용을 UTF-8로 인코딩하여 업로드
        blob_client.upload_blob(content.encode('utf-8'), overwrite=True)

        return blob_client.url
    except Exception as e:
        logging.error(f"결과 저장 중 오류 발생: {e}")
        return f"Error: {str(e)}"