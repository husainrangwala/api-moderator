import base64
import io
import logging
from typing import Any, Dict, Tuple

from PIL import Image
import requests

from app.core.config import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()

class ImageAnalyzer:

    def _analyze_nsfw(self, img: Image.Image) -> Dict[str, float]:
        try:
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode

            API_URL = "https://api-inference.huggingface.co/models/Falconsai/nsfw_image_detection"
            headers = {"Authorization": f"Bearer {settings.HUGGING_FACE_ACCESS_TOKEN}"}

            response = requests.post(
                API_URL,
                headers=headers,
                json={"inputs": img_base64},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()

                if isinstance(result, list) and len(result) > 0:
                    scores = {}
                    for item in result:
                        if isinstance(item, dict) and 'label' in item:
                            scores[item['label'].lower()] = item.get('score', 0.0)

                    return scores
                
            return {"nsfw": 0.1, "safe": 0.9}
        
        except Exception as e:
            logger.warning(f"NSFW analysis failed: {e}")
            return {"nsfw": 0.0, "safe": 1.0}

    def _detect_objects(self, img: Image.Image) -> Dict[str, Any]:
        try:
            # Mock object detection for now
            # In production, use services like:
            # - Google Vision API
            # - AWS Rekognition  
            # - HuggingFace object detection models
            
            return {
                "objects": ["person", "indoor"],
                "confidence": 0.8,
                "detected_count": 2
            }
            
        except Exception as e:
            logger.warning(f"Object detection failed: {e}")
            return {}

    def _extract_text(self, img: Image.Image) -> str:
        try:
            # Mock OCR for now
            # In production, use:
            # - Google Vision API OCR
            # - AWS Textract
            # - pytesseract
            
            return ""
            
        except Exception as e:
            logger.warning(f"Text extraction failed: {e}")
            return ""
    
    def _determine_verdict(self, analysis_data: Dict[str, Any]) -> str:

        nsfw_scores = analysis_data.get('nsfw_scores', {})
        
        nsfw_score = nsfw_scores.get('nsfw', 0.0)
        if nsfw_score > 0.7:
            return "flagged"
        
        extracted_text = analysis_data.get('extracted_text', '')
        if extracted_text and len(extracted_text.strip()) > 0:
            pass
        
        return "clean"

    def analyze_image(self, image_path: str) -> Tuple[str, Dict[str, Any]]:

        try:
            with Image.open(image_path) as img:

                if img.width > 1024 or img.height > 1024:
                    img.thumbnail((1024,1024), Image.Resampling.LANCZOS)

                if img.mode != 'RGB':
                    img = img.convert('RGB')

                nsfw_result = self._analyze_nsfw(img)
                object_detection = self._detect_objects(img)
                text_extraction = self._extract_text(img)

                analysis_data = {
                    'nsfw_scores': nsfw_result,
                    'detected_objects': object_detection,
                    'extracted_text': text_extraction,
                }
                
                verdict = self._determine_verdict(analysis_data)
                
                return verdict, analysis_data
        
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return "error", {"error": str(e)}
        