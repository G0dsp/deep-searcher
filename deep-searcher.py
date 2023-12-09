import re
import requests
import random
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

class AhmiaScraper:
    def __init__(self, max_threads=5):
        self.session = requests.Session()
        self.max_threads = max_threads
        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Log to console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Log to file
        file_handler = logging.FileHandler('ahmia_scraper.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def _clean_link(self, link):
        cleaned_link = link.split('=')[-1].strip()
        return cleaned_link[len("/blacklist/report?onion="):] if cleaned_link.startswith("/blacklist/report?onion=") else cleaned_link

    def _get(self, url):
        try:
            with self.session.get(url, headers=self._get_headers(), timeout=10) as response:
                response.raise_for_status()
                return response.text

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making request to {url}: {e}")
            return None

    def _get_headers(self):
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_single(self, query):
        try:
            formatted_query = query.replace(" ", "+")
            url = f"https://ahmia.fi/search/?q={formatted_query}"
            content = self._get(url)

            if content:
                regex_query = r'<a href="(.*?)"'
                links = set(re.findall(regex_query, content))
                cleaned_links = [self._clean_link(link) for link in links]
                return cleaned_links
            else:
                return []

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error processing query '{query}': {e}")
            return []

    def scrape(self, query_list, output_filename=None):
        try:
            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                results = list(executor.map(self.scrape_single, query_list))

            all_cleaned_links = set(link for sublist in results for link in sublist)

            filename = output_filename or f"sites_{random.randint(1, 9999)}.txt"
            self.logger.info(f"Saving to {filename}")

            with Path(filename).open("w") as file:
                file.write("\n".join(all_cleaned_links))

            self.logger.info("All the links written to a text file:", filename)

            with Path(filename).open() as file:
                head = [next(file) for _ in range(5)]
                contents = "\n".join(map(str, head))
                self.logger.info(contents)

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error: {e}")

if __name__ == "__main__":
    try:
        max_threads = int(input("[*] Enter the maximum number of threads (default is 5): ") or 5)
    except ValueError:
        max_threads = 5

    user_queries = input("[*] Please Enter Your Queries (comma-separated): ").split(',')
    output_filename = input("[*] Enter Output Filename (press Enter for default): ")

    scraper = AhmiaScraper(max_threads=max_threads)
    scraper.scrape(user_queries, output_filename)
