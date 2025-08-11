import logging
import requests

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
# HF_API_URL = "https://api-inference.huggingface.co/models/martin-ha/toxic-comment-model"
HF_API_URL = "https://api-inference.huggingface.co/models/unitary/toxic-bert"
headers = {"Authorization": f"Bearer {settings.HUGGING_FACE_ACCESS_TOKEN}"}

def check_text_hf(content: str):
    try:
        if not content.strip():
            return "clean", {}
        
        response = requests.post(HF_API_URL, headers=headers, json={"inputs": content})
        response.raise_for_status()

        result = response.json()
        logger.info(f"HF API Response: {result}")

        if isinstance(result, list) and len(result) > 0:
            first_result = result[0]

            if isinstance(first_result, list):
                predictions = first_result
            
            elif isinstance(first_result, dict):
                predictions = result

            else:
                logger.error(f"Unexpected response format: {result}")
                return "error", {"error": "Unexpected API response format"}
            
            scores = {}
            max_score = 0.0
            flagged_categories = []

            for item in predictions:
                if isinstance(item, dict) and "label" in item or "score" in item:

                    label = item["label"].lower()
                    score = float(item["score"])
                    scores[label] = score

                    max_score = max(max_score, score)

                    if max_score > 0.3:
                        flagged_categories.append(label)

            verdict = "flagged" if flagged_categories else "clean"
            logger.info(f"Moderation result: {verdict}, max_score: {max_score}")
            return verdict, scores
        
        else:
            logger.error(f"Invalid API response: {result}")
            return "error", {"error": "Invalid API response"}
    
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP request failed: {e}")
        return "error", {"error": f"API request failed: {str(e)}"}
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return "error", {"error": "Moderation service temporarily unavailable"}
