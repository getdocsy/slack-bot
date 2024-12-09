from loguru import logger
import textwrap
from docsy.engine.scraper import Scraper
from docsy.engine.ai.base import BaseAI


class AI(BaseAI):

    def analyze(self, url: str) -> str:
        """
        Analyze a URL and return suggestions.
        """
        scraper = Scraper()
        content = scraper.scrape(url)
        nav_elements = scraper.extract_navigation_elements(url)

        prompt = self.base_prompt + [
            {
                "role": "user",
                "content": f"Please analyze this URL and provide suggestions: {url}. The content of the page is: {content}",
            },
            {
                "role": "user",
                "content": f"The navigation elements of the page are: {nav_elements}",
            },
        ]
        logger.info("Prompt:")
        for msg in prompt:
            logger.info(f"{msg['role']}: {msg['content']}")
        # return self._get_suggestion(prompt)


if __name__ == "__main__":
    ai = AI()
    print(ai.analyze("https://docs.getdocsy.com"))
