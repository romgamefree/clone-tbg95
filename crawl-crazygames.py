import os
import time
import logging
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import WebDriverException
import requests
from bs4 import BeautifulSoup

class WebsiteDownloaderWithScroll:
    def __init__(self, base_url, output_dir='cloned_site', max_depth=5, scroll_pause_time=2, max_retries=3, retry_delay=5):
        self.base_url = base_url.rstrip('/')
        self.output_dir = output_dir
        self.max_depth = max_depth
        self.scroll_pause_time = scroll_pause_time
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.visited_urls = set()
        self.downloaded_files = set()
        self.failed_urls = set()

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Configure Chrome WebDriver with enhanced network settings
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-cache")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-application-cache")
        chrome_options.add_argument("--disable-network-throttling")
        chrome_options.add_argument("--dns-prefetch-disable")

        # Add network conditions
        caps = DesiredCapabilities.CHROME.copy()
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        
        chrome_service = Service(log_path=os.devnull)
        self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options, desired_capabilities=caps)
        
        # Set page load timeout
        self.driver.set_page_load_timeout(30)

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        # Error log file
        self.error_log_file = os.path.join(self.output_dir, "error_log.txt")
        with open(self.error_log_file, 'w', encoding='utf-8') as f:
            f.write("=== Error Log ===\n")

    def log_error(self, url, error_message):
        """Write errors to log file"""
        with open(self.error_log_file, 'a', encoding='utf-8') as f:
            f.write(f"{url} - Error: {error_message}\n")
        self.logger.error(f"Error {url}: {error_message}")
        self.failed_urls.add(url)

    def reset_driver(self):
        """Reset the WebDriver if it becomes unresponsive"""
        try:
            self.driver.quit()
        except:
            pass
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-cache")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-application-cache")
        chrome_options.add_argument("--disable-network-throttling")
        chrome_options.add_argument("--dns-prefetch-disable")
        
        caps = DesiredCapabilities.CHROME.copy()
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        
        self.driver = webdriver.Chrome(service=Service(log_path=os.devnull), options=chrome_options, desired_capabilities=caps)
        self.driver.set_page_load_timeout(30)

    def scroll_to_bottom(self):
        """Scroll to the bottom of the page"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(self.scroll_pause_time)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        except Exception as e:
            self.logger.warning(f"Error during scrolling: {str(e)}")

    def fetch_page_with_retry(self, url):
        """Fetch page with retry logic"""
        for attempt in range(self.max_retries):
            try:
                self.driver.get(url)
                self.logger.info(f"Loading page (attempt {attempt + 1}): {url}")

                # Scroll to bottom to load all dynamic content
                self.scroll_to_bottom()

                # Wait for essential resources
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, 'body'))
                )

                return self.driver.page_source

            except WebDriverException as e:
                if "ERR_INTERNET_DISCONNECTED" in str(e):
                    self.logger.warning(f"Network error on attempt {attempt + 1} for {url}. Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                    
                    # Reset the driver if we're not on the last attempt
                    if attempt < self.max_retries - 1:
                        self.reset_driver()
                    continue
                else:
                    self.log_error(url, str(e))
                    return None

            except Exception as e:
                self.log_error(url, str(e))
                return None

        self.log_error(url, f"Failed after {self.max_retries} attempts")
        return None

    def save_resource(self, url, content):
        """Save webpage HTML to file with correct path handling"""
        try:
            parsed_url = urlparse(url)
            
            # Remove 'www.' from the path if present
            domain = parsed_url.netloc.replace('www.', '')
            
            # Construct the relative path from the URL path
            url_path = parsed_url.path.lstrip('/')
            if not url_path:
                url_path = 'index.html'
            elif not url_path.endswith('.html'):
                url_path = os.path.join(url_path, 'index.html')

            # Combine output directory, domain, and URL path
            full_path = os.path.join(self.output_dir, domain, url_path)
            
            # Normalize the path separators for the current OS
            full_path = os.path.normpath(full_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # Save the file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.downloaded_files.add(full_path)
            self.logger.info(f"Saved page: {full_path}")
            return full_path
        except Exception as e:
            self.log_error(url, f"Error saving resource: {e}")
            return None

    def extract_links(self, html, base_url):
        """Extract links from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = set()

            for a_tag in soup.find_all('a', href=True):
                link = urljoin(base_url, a_tag['href'])
                if link.startswith(self.base_url):
                    links.add(link)

            return links
        except Exception as e:
            self.logger.warning(f"Error extracting links from {base_url}: {str(e)}")
            return set()

    def crawl(self, url, depth=0):
        """Crawl and download content from URL with improved error handling"""
        if url in self.visited_urls or depth > self.max_depth or url in self.failed_urls:
            return

        self.visited_urls.add(url)
        self.logger.info(f"Crawling: {url}")

        # Load page and save content with retry logic
        html = self.fetch_page_with_retry(url)
        if html:
            saved_path = self.save_resource(url, html)
            if saved_path:
                # Extract links and continue crawling
                links = self.extract_links(html, url)
                for link in links:
                    self.crawl(link, depth + 1)

    def run(self):
        """Run the entire process with cleanup"""
        try:
            self.logger.info(f"Starting crawl of {self.base_url}")
            self.crawl(self.base_url)
            
            # Log summary
            self.logger.info(f"Crawling completed. Successfully visited {len(self.downloaded_files)} pages.")
            if self.failed_urls:
                self.logger.warning(f"Failed to crawl {len(self.failed_urls)} URLs.")
                
        except Exception as e:
            self.logger.error(f"Critical error during crawl: {str(e)}")
        finally:
            try:
                self.driver.quit()
            except:
                pass


if __name__ == '__main__':
    base_url = "https://www.crazygames.com/"  # Base URL to crawl
    output_dir = "crazygames_cloned_site"     # Directory to save downloaded pages
    max_depth = 5                             # Maximum crawl depth
    max_retries = 3                           # Number of retry attempts
    retry_delay = 5                           # Seconds to wait between retries

    downloader = WebsiteDownloaderWithScroll(
        base_url=base_url,
        output_dir=output_dir,
        max_depth=max_depth,
        max_retries=max_retries,
        retry_delay=retry_delay
    )
    downloader.run()