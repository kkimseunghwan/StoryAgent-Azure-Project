
import logging
from unittest import result
import azure.durable_functions as df
import os
from azure.storage.blob import BlobServiceClient

# 오케스트라 함수 정의
def orchestrator_function(context: df.DurableOrchestrationContext):
    
    # 1. Event Grid로부터 파일 정보가 담긴 데이터를 받음.
    event_data = context.get_input()
    task_id = event_data.get("task_id")

    # path_parts = file_url.split('/')[3:] 
    # file_name = path_parts[-1]
    # task_id = path_parts[-2]

    # activity_input  = {
    #     "file_url": file_url,
    #     "file_name": file_name,
    #     "task_id": task_id
    # }

    # task_id 폴더의 파일 목록을 조회
    try:
        connect_str = os.environ["FILE_STORAGE_CONNECTION_STRING"]
        blob_service_client = BlobServiceClient.from_connection_string(conn_str=connect_str)
        container_name = "request-files"
        container_client = blob_service_client.get_container_client(container_name)
        
        blob_list = container_client.list_blobs(name_starts_with=task_id)
        
        # 처리할 파일들의 URL과 이름을 리스트에 저장
        files_to_process = [
            {"name": blob.name.split('/')[-1], "url": f"{container_client.url}/{blob.name}"}
            for blob in blob_list
        ]

    except Exception as e:
        logging.error(f"Error listing blobs for task_id {task_id}: {e}")
        return f"Error listing blobs: {str(e)}"

    if not files_to_process:
        logging.warning(f"No files found for task_id: {task_id}")
        return "No files found to process."




    tasks = []
    for file_info in files_to_process:
        file_name = file_info["name"]
        file_url = file_info["url"]

        activity_input  = {
            "file_url": file_url,
            "file_name": file_name,
            "task_id": task_id
        }

        # 파일 확장자에 따라 작업을 분기
        if file_name.endswith(('.mp3', '.wav')):
            # 'TranscribeAudioActivity' 라는 이름의 Activity 함수를 호출
            tasks.append(context.call_activity("TranscribeAudioActivity", activity_input ))
        
        elif file_name.endswith(('.txt', '.csv')):
            # 'ReadTextFileActivity' 라는 이름의 Activity 함수를 호출
            tasks.append(context.call_activity("ReadTextFileActivity", activity_input ))


        # TODO: PDF, 이미지 등 다른 파일 형식에 대한 처리 추가

    if tasks:
        # 모든 작업들을 병렬로 실행하고 결과를 기다림
        results = yield context.task_all(tasks)
        combined_text = "\n".join(results)

        # 결과 저장할 데이터 구성 JSON
        data_to_save = {
            "task_id": task_id,
            "content": combined_text
        }

        # 텍스트 저장 Activity 호출
        final_url = yield context.call_activity("SaveTextToBlobActivity", data_to_save)

        # 작업 종료
        return {"message": "Orchestration for specific file type completed.", "output_url": final_url}
    else:
        return {"message": "No supported files found to process."}


main = df.Orchestrator.create(orchestrator_function)
