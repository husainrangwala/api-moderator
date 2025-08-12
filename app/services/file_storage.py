import hashlib
import logging

from pathlib import Path
from typing import Tuple
import uuid
from PIL import Image
import magic


logger = logging.getLogger(__name__)

class FileStorageService:

    def __init__(self, upload_dir: str = 'uploads/images'):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        self.allowed_types = {
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
            'image/webp', 'image/bmp', 'image/tiff'
        }

        self.max_file_size = 10 * 1024 * 1024

    def _get_image_dimensions(self, file_path: Path) -> dict:

        try:
            with Image.open(file_path) as img:
                return {"width": img.width, "height": img.height}
        except Exception as e:
            logger.warning(f"Could not get dimensions for {file_path}: {e}")
            return {}

    def save_uploaded_file(self, file_content: bytes, filename: str) -> Tuple[str, dict]:

        try:
            if len(file_content) > self.max_file_size:
                raise ValueError(f"File is too large: {len(file_content)} bytes")

            file_type = magic.from_buffer(file_content, mime=True)
            if file_type not in self.allowed_types:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            file_extension = Path(filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = self.upload_dir / unique_filename

            with open(file_path, "wb") as f:
                
                f.write(file_content)

                dimensions = self._get_image_dimensions(file_path)

                file_hash = hashlib.sha256(file_content).hexdigest()

                metadata = {
                    "file_path": str(file_path),
                    "file_size": len(file_content),
                    "file_type": file_type,
                    "dimensions": dimensions,
                    "file_hash": file_hash,
                    "original_filename": filename
                }

                logger.info(f"Saved file: {unique_filename}, size: {len(file_content)}, type: {file_type}")

                return str(file_path), metadata
            
        except Exception as e:
            logger.error(f"File save failed: {e}")
            raise

    def delete_file(self, file_path: str) -> bool:

        try:
            Path(file_path).unlink(missing_ok=True)
            return True
        
        except Exception as e:
            logger.info("File deletion failed: {e}")
            return False
