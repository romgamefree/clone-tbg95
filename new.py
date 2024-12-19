import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import concurrent.futures
import random
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class WebsiteCrawler:
    def __init__(self, base_url, output_dir='cloned_site', max_depth=5):
        self.base_url = base_url.rstrip('/')
        self.output_dir = output_dir
        self.max_depth = max_depth
        self.visited_urls = set()
        self.session = requests.Session()
        self.failed_urls = []

        # User-Agent rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]

        # Logging configuration
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Selenium setup
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(), options=chrome_options)

    def get_random_headers(self):
        """Generate random headers to avoid being blocked"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': self.base_url,
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def save_resource(self, url, content, is_binary=False):
        """Save resource to disk"""
        try:
            parsed_url = urlparse(url)
            path = os.path.join(
                self.output_dir, 
                parsed_url.netloc, 
                parsed_url.path.lstrip('/').replace('/', os.sep)
            )

            os.makedirs(os.path.dirname(path), exist_ok=True)

            if path.endswith('/') or not os.path.splitext(path)[1]:
                path = os.path.join(path, 'index.html')

            with open(path, 'wb' if is_binary else 'w', encoding=None if is_binary else 'utf-8') as f:
                f.write(content)

            return path
        except Exception as e:
            self.logger.error(f"Failed to save resource {url}: {e}")
            return None

    def extract_links(self, html, base_url):
        """Extract links from HTML"""
        soup = BeautifulSoup(html, 'lxml')
        links = set()

        for attr, tag in [
            ('href', ['a', 'link']), 
            ('src', ['img', 'script', 'iframe', 'source'])
        ]:
            for element in soup.find_all(tag):
                link = element.get(attr)
                if link:
                    full_url = urljoin(base_url, link)
                    if full_url.startswith(self.base_url):
                        links.add(full_url)

        return links

    def scroll_to_bottom(self, url):
        """Scroll to the bottom of the page to load all dynamic content"""
        try:
            self.driver.get(url)
            time.sleep(2)
            while True:
                old_height = self.driver.execute_script("return document.body.scrollHeight")
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                time.sleep(2)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == old_height:
                    break

            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"Failed to scroll {url}: {e}")
            return None

    def download_resource(self, url):
        """Download a resource (e.g., CSS, JS, images)"""
        try:
            response = self.session.get(
                url, 
                headers=self.get_random_headers(), 
                timeout=10
            )

            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '').lower()
                is_binary = 'text/html' not in content_type
                self.save_resource(url, response.content if is_binary else response.text, is_binary)
                return True
        except Exception as e:
            self.logger.error(f"Failed to download resource {url}: {e}")

        self.failed_urls.append(url)
        return False

    def clone_website(self):
        """Main website cloning process"""
        os.makedirs(self.output_dir, exist_ok=True)

        urls_to_visit = {self.base_url}
        visited_depth = {self.base_url: 0}

        while urls_to_visit:
            url = urls_to_visit.pop()

            if url in self.visited_urls or visited_depth.get(url, 0) > self.max_depth:
                continue

            self.logger.info(f"Cloning: {url}")

            try:
                page_source = self.scroll_to_bottom(url)

                if not page_source:
                    self.failed_urls.append(url)
                    continue

                self.save_resource(url, page_source)
                self.visited_urls.add(url)

                links = self.extract_links(page_source, url)
                for link in links:
                    if link not in self.visited_urls:
                        urls_to_visit.add(link)
                        visited_depth[link] = visited_depth.get(url, 0) + 1

                resources = [
                    link for link in links 
                    if any(link.endswith(ext) for ext in ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf'])
                ]

                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    executor.map(self.download_resource, resources)

                time.sleep(random.uniform(0.5, 2))

            except Exception as e:
                self.logger.error(f"Failed to clone {url}: {e}")
                self.failed_urls.append(url)

        with open(os.path.join(self.output_dir, 'failed_urls.txt'), 'w') as f:
            f.write('\n'.join(self.failed_urls))

        print("Website cloning complete!")

def main():
    base_url = 'https://tbg95.github.io/'
    cloner = WebsiteCrawler(base_url, max_depth=10)
    cloner.clone_website()

if __name__ == '__main__':
    main()
