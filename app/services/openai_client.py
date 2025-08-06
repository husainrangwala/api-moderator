import logging
from typing import Any, Dict, Tuple

import openai

from app.core.config import get_settings


logger = logging.getLogger(__name__)

settings = get_settings()
openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

def check_text(content: str) -> Tuple[str, Dict[str, Any]]:
    try:
        if not content.strip():
            return "clean", {}
        
        response = openai_client.moderations.create(
            input=content,
            model="text-moderation-latest"
        )

        result = response.results[0]

        verdict = "flagged" if result.flagged else "clean"

        scores = dict(
            result.category_scores.model_dump()
        ) if hasattr(result.category_scores, 'model_dump') else dict(result.category_scores)

        logger.info(f"Moderated text (length: {len(content)}): verdict: {verdict}")

        return verdict, scores
    
    except openai.APIError as e:
        logger.error(f"OpenAI Error {e}")

        return "error", {"error": str(e)}
    
    except Exception as e:
        logger.error("Encountered an unexpected error: ${e}")

        return "error", {"error": "Service unavailable"}
    