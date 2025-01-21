import logging
from typing import Optional, Dict
from litellm import completion
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TitleGenerator:
    def __init__(self):
        self.max_words = 10
        self.min_words = 3
        self.default_prefix = "Rule"

    def _clean_title(self, title: str) -> str:
        """Clean and format the generated title"""
        # Remove any special characters except alphanumeric and basic punctuation
        title = re.sub(r'[^\w\s\-:,]', '', title)
        # Remove extra whitespace
        title = ' '.join(title.split())
        # Capitalize first letter of each word
        title = title.title()
        return title

    def _validate_title(self, title: str) -> bool:
        """Check if the title meets basic requirements"""
        if not title:
            return False

        words = title.split()
        if len(words) < self.min_words or len(words) > self.max_words:
            return False

        # Check if title contains meaningful words
        meaningful_words = [w for w in words if len(w) > 2]
        return len(meaningful_words) >= 2

    def _extract_key_terms(self, context: str) -> list:
        """Extract key terms from the context for backup title generation"""
        # Split into lines and take first few non-empty lines
        lines = [line.strip() for line in context.split('\n') if line.strip()]
        if not lines:
            return []

        # Take first line and extract key terms
        first_line = lines[0]
        # Remove common words and keep meaningful terms
        terms = re.findall(r'\b\w+\b', first_line)
        return [term for term in terms if len(term) > 3][:5]

    def _generate_backup_title(self, context: str) -> str:
        """Generate a backup title when API generation fails"""
        terms = self._extract_key_terms(context)
        if terms:
            title = ' '.join(terms[:4])
            return f"{self.default_prefix}: {title}"
        return f"{self.default_prefix} {context[:30].strip()}..."

    async def generate_title_async(self, context: str) -> str:
        """
        Generate a title asynchronously using Gemini
        """
        prompt = f"""
        Create a concise and descriptive title (3-10 words) for a rule with the following context.
        The title should be clear, professional, and capture the main purpose of the rule.

        Context:
        {context}

        Requirements:
        - Title should be 3-10 words
        - Must be clear and descriptive
        - Should capture the main focus of the rule
        - Use professional language
        - Only return the title, nothing else
        """

        try:
            logger.debug(f"{__name__}.generate_title_async() started")
            response = completion(
                model="gemini/gemini-1.5-flash",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50
            )
            logger.info(response)
            title = response.choices[0].message.content.strip()
            title = self._clean_title(title)

            if self._validate_title(title):
                return title

            logger.warning("Generated title failed validation, using backup method")
            return self._generate_backup_title(context)

        except Exception as e:
            logger.error(f"Error generating title: {str(e)}")
            return self._generate_backup_title(context)


def generate_title(context: str) -> str:
    """
    Synchronous wrapper for title generation
    """
    import asyncio

    generator = TitleGenerator()
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    title = loop.run_until_complete(generator.generate_title_async(context))
    return title