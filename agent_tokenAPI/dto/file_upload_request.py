from pydantic import BaseModel

class FileUploadRequest(BaseModel):
    filename: str
    content_type: str
    task_id: str