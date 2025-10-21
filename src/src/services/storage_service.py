from pathlib import Path
import aiofiles
from fastapi import UploadFile
from src.core.config import settings

class StorageService:
    def __init__(self):
        self.base = Path("uploads")
        self.base.mkdir(parents=True, exist_ok=True)

    async def upload_uploadfile(self, upload: UploadFile, dest_rel: str) -> str:
        dest = self.base / dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(dest, "wb") as f:
            while True:
                chunk = await upload.read(1024 * 1024)
                if not chunk:
                    break
                await f.write(chunk)
        return str(dest.resolve())
