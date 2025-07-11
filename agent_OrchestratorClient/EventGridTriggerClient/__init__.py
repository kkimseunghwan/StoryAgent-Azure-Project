import logging
import azure.functions as func
import azure.durable_functions as df

# Event Grid 이벤트를 받아 Orchestrator를 시작시키는 Client 함수
async def main(event: func.EventGridEvent, starter: str):

    client = df.DurableOrchestrationClient(starter)
    
    event_data = event.get_json()
    logging.info(f"Event Grid trigger received event: {event_data}")

    # 'FileProcessingOrchestrator' 이름의 오케스트레이션을 시작시킵니다.
    # 이벤트 데이터를 그대로 오케스트레이터의 입력값으로 전달합니다.
    instance_id = await client.start_new("FileProcessingOrchestrator", None, event_data)

    logging.info(f"Started orchestration with ID = '{instance_id}'.")