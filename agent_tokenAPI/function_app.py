

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from dto.file_upload_request import FileUploadRequest
import azure.functions as func
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta, timezone
import logging
import uuid
import os

fast_app = FastAPI()
fast_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app = func.AsgiFunctionApp(app=fast_app, http_auth_level=func.AuthLevel.ANONYMOUS)

# Blob Storage 연결 문자열
AZURE_CONNECTION_STRING = os.environ['STORAGE_CONNECTION_STRING']
# 사용할 컨테이너 이름
CONTAINER_NAME = "request-files"

# 테스트
# @fast_app.get("/storage/SAS/token")
# async def get_sas_token(request: FileUploadRequest):
#     return request


# SAS 토큰이 포함된 파일 업로드 URL을 생성하여 반환
@fast_app.post("/generate-upload-url")
async def generate_upload_url(request: FileUploadRequest):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

        # TODO: 동시 처리 시 id가 중복되는 경우가 있을 수 있으므로, 후에 중복 처리 로직 추가 필요
        task_id = str(uuid.uuid4())
        blob_name = f"{task_id}/{request.filename}"

        # SAS 토큰 생성 (10분 동안 유효, 쓰기 권한)
        sas_token = generate_blob_sas(
            account_name=blob_service_client.account_name,
            container_name=CONTAINER_NAME,
            blob_name=blob_name,
            account_key=blob_service_client.credential.account_key,
            permission=BlobSasPermissions(write=True),
            expiry=datetime.now(timezone.utc) + timedelta(minutes=10)
        )

        upload_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{CONTAINER_NAME}/{blob_name}?{sas_token}"

        return {"task_id": task_id, "upload_url": upload_url, "filename": request.filename}

    except Exception as e:
        return {"error": str(e)}, 500