
import logging
from unittest import result
import azure.durable_functions as df

# 오케스트라 함수 정의
def orchestrator_function(context: df.DurableOrchestrationContext):
    
    # 1. Event Grid로부터 파일 정보가 담긴 데이터를 받음.
    event_data = context.get_input()
    file_url = event_data.get("url")

    path_parts = file_url.split('/')[3:] 
    file_name = path_parts[-1]
    task_id = path_parts[-2]

    activity_input  = {
        "file_url": file_url,
        "file_name": file_name,
        "task_id": task_id
    }

    tasks = []

    # 파일 확장자에 따라 작업을 분기
    if file_name.endswith(('.mp3', '.wav')):
        # 'TranscribeAudioActivity' 라는 이름의 Activity 함수를 호출
        tasks.append(context.call_activity("TranscribeAudioActivity", activity_input ))
    
    elif file_name.endswith(('.txt', '.csv')):
        # 'ReadTextFileActivity' 라는 이름의 Activity 함수를 호출
        tasks.append(context.call_activity("ReadTextFileActivity", activity_input ))


    # TODO: PDF, 이미지 등 다른 파일 형식에 대한 처리 추가

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

main = df.Orchestrator.create(orchestrator_function)
