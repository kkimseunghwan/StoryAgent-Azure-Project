import logging
import azure.functions as func
import azure.durable_functions as df

async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    client = df.DurableOrchestrationClient(starter)

    # HTTP 요청의 본문을 그대로 오케스트레이터의 입력값으로 사용합니다.
    input_data = req.get_json()

    instance_id = await client.start_new("FileProcessingOrchestrator", None, input_data)
    logging.info(f"Started orchestration with ID = '{instance_id}'.")

    return client.create_check_status_response(req, instance_id)