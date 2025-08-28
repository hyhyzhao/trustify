# ai_module/text_analyzer.py
import logging
from .providers.azure_client import AzureContentSafetyProvider
# Future: from .providers.huggingface_client import HuggingFaceProvider

logger = logging.getLogger(__name__)

class TextAnalyzer:
    """
    Unified text analysis entry point.
    Responsible for selecting and using different AI providers,
    and returning a consistent interface for the frontend.
    """

    def __init__(self, provider: str = 'azure'):
        """
        Initialize the text analyzer.

        Args:
            provider (str): AI provider to use. Currently supports 'azure'.
        """
        self.provider = provider.lower()
        self._initialize_provider()

    def _initialize_provider(self):
        """Initialize the specific AI provider based on the configuration."""
        try:
            if self.provider == 'azure':
                self._client = AzureContentSafetyProvider()
                logger.info(f"Initialized with provider: {self.provider}")
            # Future: add other providers
            # elif self.provider == 'huggingface':
            #     self._client = HuggingFaceProvider()
            else:
                raise ValueError(f"Unsupported provider: {self.provider}. Choose 'azure'")
        except Exception as e:
            logger.error(f"Failed to initialize {self.provider} provider: {e}")
            raise

    def analyze(self, text: str) -> dict:
        """
        Main method to analyze text content.

        Args:
            text (str): The input text to analyze.

        Returns:
            dict: Standardized analysis result:
                - is_harmful (bool): Whether harmful content is detected.
                - risk_level (str): Overall risk level ('Safe', 'Low', 'Medium', 'High').
                - categories (dict): Category -> severity level mapping.
                - confidence_scores (dict): Category -> confidence score (0-1).
                - provider (str): The provider used for analysis.
                - error (str or None): Error message if any occurred.
        """
        if not text or not isinstance(text, str):
            return {
                'is_harmful': False,
                'risk_level': 'Safe',
                'categories': {},
                'provider': self.provider,
                'error': 'Invalid input: text must be a non-empty string'
            }

        try:
            # Call the specific provider's analysis method
            raw_result = self._client.analyze_text(text)
            # Standardize the output format
            standardized_result = self._standardize_result(raw_result)
            return standardized_result

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                'is_harmful': False,
                'risk_level': 'Unknown',
                'categories': {},
                'provider': self.provider,
                'error': f'Analysis service unavailable: {str(e)}'
            }

    def _standardize_result(self, raw_result: dict) -> dict:
        """
        Convert provider-specific results into a unified format.

        """
        if raw_result.get('error'):
            return {
                'is_harmful': False,
                'risk_level': 'Unknown',
                'categories': {},
                'provider': self.provider,
                'error': raw_result['error']
            }

        risk_level = self._calculate_overall_risk(raw_result['categories'])

        return {
            'is_harmful': raw_result['is_harmful'],
            'risk_level': risk_level,
            'categories': raw_result['categories'],
            'confidence_scores': raw_result.get('confidence_scores', {}),
            'provider': self.provider,
            'error': None
        }

    def _calculate_overall_risk(self, categories: dict) -> str:
        """
        Determine the overall risk level based on category results.

        """
        risk_mapping = {'Safe': 0, 'Low': 1, 'Medium': 2, 'High': 3}
        max_risk = max((risk_mapping.get(level, 0) for level in categories.values()), default=0)

        reverse_mapping = {0: 'Safe', 1: 'Low', 2: 'Medium', 3: 'High'}
        return reverse_mapping[max_risk]

# Global instance
default_analyzer = TextAnalyzer()

def analyze_text(text: str, provider: str = 'azure') -> dict:
    """
    Convenience function: quickly analyze text using a specified provider.
    """
    analyzer = TextAnalyzer(provider=provider)
    return analyzer.analyze(text)
