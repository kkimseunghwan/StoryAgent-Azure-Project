
import logging
import azure.durable_functions as df

# 오케스트라 함수 정의
def orchestrator_function(context: df.DurableOrchestrationContext):
    
    # 1. Event Grid로부터 파일 정보가 담긴 데이터를 받음.
    event_data = context.get_input()
    logging.info(f"Orchestrator가 다음 입력값으로 시작되었습니다: {event_data}")

    file_url = event_data.get("url")

    path_parts = file_url.split('/')[3:] 
    file_name = path_parts[-1]
    task_id = path_parts[-2]

    activity_input  = {
        "file_url": file_url,
        "file_name": file_name,
        "task_id": task_id
    }

    # 파일 확장자에 따라 작업을 분기
    if file_name.endswith(('.mp3', '.wav')):
        # 'TranscribeAudioActivity' 라는 이름의 Activity 함수를 호출합니다.
        result = yield context.call_activity("TranscribeAudioActivity", activity_input )
    
    else:
        result = f"Unsupported file type: {file_name}"

    # TODO: 다른 파일 형식의 Activity 함수를 호출하는 코드를 추가할 예정.
    # elif file_name.endswith('.pdf'):
    #     # 'ExtractTextFromPdfActivity' 라는 이름의 Activity 함수를 호출합니다.
    #     result = yield context.call_activity("ExtractTextFromPdfActivity", file_url)

    # elif file_name.endswith(('.png', '.jpg')):
    #     # 'ProcessImageActivity' 라는 이름의 Activity 함수를 호출합니다.
    #     result = yield context.call_activity("ProcessImageActivity", file_url)

    # 3. 모든 작업이 끝난 후 결과를 반환합니다.
    return "Orchestration for specific file type completed."

main = df.Orchestrator.create(orchestrator_function)
