import json
import os
from typing import Dict, Any
from src.interfaces import IFileService

class FileService(IFileService):
    def save_metadata(self, metadata: Dict[str, Any], out_path: str) -> str:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        return out_path
