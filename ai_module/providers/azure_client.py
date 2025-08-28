# ai_module/providers/azure_client.py
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety import ContentSafetyClient
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class AzureContentSafetyProvider:
    """Concrete implementation of Azure Content Safety"""

    def __init__(self):
        key = os.getenv("AZURE_CONTENT_SAFETY_KEY")
        endpoint = os.getenv("AZURE_CONTENT_SAFETY_ENDPOINT")

        if not key or not endpoint:
            raise ValueError("Missing Azure Content Safety credentials")

        self.client = ContentSafetyClient(endpoint, AzureKeyCredential(key))
        logger.info("Azure Content Safety provider initialized")

    def analyze_text(self, text_content: str):
        """
        Analyze text and return a standardized result.

        Returns:
            dict: {
                'is_harmful': bool,
                'categories': {str: str}, # category -> severity level
                'confidence_scores': {str: float},# category -> normalized severity (0-1)
                'provider': 'azure',
                'error': str or None
            }
        """
        result = {
            'is_harmful': False,
            'categories': {},
            'confidence_scores': {},
            'provider': 'azure',
            'error': None
        }

        if not text_content or not text_content.strip():
            result['error'] = "Input text is empty"
            return result

        try:
            request = {"text": text_content}
            response = self.client.analyze_text(request)

            for category in response.categories_analysis:
                category_name = category.category if isinstance(category.category, str) else category.category.name
                severity = category.severity

                result['categories'][category_name] = self._severity_to_level(severity)
                result['confidence_scores'][category_name] = severity / 7.0

                if severity > 0:
                    result['is_harmful'] = True

        except Exception as e:
            logger.error(f"Azure API error: {e}")
            result['error'] = str(e)

        return result

    def _severity_to_level(self, severity: int) -> str:
        """
        Convert numeric severity to human-readable level.
        Severity levels:
            0 -> Safe
            1-2 -> Low
            3-4 -> Medium
            5-7 -> High
        """
        levels = ['Safe', 'Low', 'Low', 'Medium', 'Medium', 'High', 'High', 'High']
        return levels[severity] if 0 <= severity < len(levels) else 'Unknown'
