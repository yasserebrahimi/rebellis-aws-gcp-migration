from pydantic import BaseModel
from datetime import datetime

class UploadResponse(BaseModel):
    file_id: str
    file_path: str
    file_size: int
    content_type: str
    uploaded_at: datetime = datetime.utcnow()
