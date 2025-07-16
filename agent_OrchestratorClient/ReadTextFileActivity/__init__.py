import logging
import os
from azure.storage.blob import BlobClient

def main(activity_input: dict) -> str:

    file_url = activity_input.get('file_url')
    file_name = activity_input.get('file_name')
    task_id = activity_input.get('task_id')

    logging.info(f"텍스트 파일 처리 시작 [id:{task_id}] {file_url}")
    try:
        container_name = "request-files"
        
        blob_client = BlobClient.from_connection_string(
            conn_str=os.environ["FILE_STORAGE_CONNECTION_STRING"],
            container_name=container_name,
            blob_name=f"{task_id}/{file_name}"
        )

        # 파일을 UTF-8 인코딩으로 다운로드하여 텍스트로 읽습니다.
        text_content = blob_client.download_blob(encoding='UTF-8').readall()

        return text_content
    except Exception as e:
        logging.error(f"텍스트 파일 처리 중 오류 발생: {e}")
        return f"Error: {str(e)} URL : {file_url}"
    


