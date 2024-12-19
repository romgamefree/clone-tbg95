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
import requests
from bs4 import BeautifulSoup

class WebsiteDownloaderWithScroll:
    def __init__(self, base_url, output_dir='cloned_site', max_depth=5, scroll_pause_time=2):
        self.base_url = base_url.rstrip('/')
        self.output_dir = output_dir
        self.max_depth = max_depth
        self.scroll_pause_time = scroll_pause_time
        self.visited_urls = set()
        self.downloaded_files = set()

        # Cấu hình logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Cấu hình Selenium WebDriver (Chrome)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Chạy ở chế độ không giao diện
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-cache")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-application-cache")

        # Tắt log của ChromeDriver
        chrome_service = Service(log_path=os.devnull)
        self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

        # Đảm bảo thư mục output tồn tại
        os.makedirs(self.output_dir, exist_ok=True)

        # Tệp log lỗi
        self.error_log_file = os.path.join(self.output_dir, "error_log.txt")
        with open(self.error_log_file, 'w', encoding='utf-8') as f:
            f.write("=== Error Log ===\n")

    def log_error(self, url, error_message):
        """Ghi lỗi vào tệp log"""
        with open(self.error_log_file, 'a', encoding='utf-8') as f:
            f.write(f"{url} - Error: {error_message}\n")
        self.logger.error(f"Lỗi {url}: {error_message}")

    def scroll_to_bottom(self):
        """Cuộn xuống cuối trang"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Cuộn xuống cuối trang
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.scroll_pause_time)  # Đợi trang tải thêm nội dung

            # Kiểm tra chiều cao mới
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:  # Không có thay đổi, dừng cuộn
                break
            last_height = new_height

    def fetch_page(self, url):
        """Tải trang web và đợi tải tài nguyên"""
        try:
            self.driver.get(url)
            self.logger.info(f"Đang tải trang: {url}")

            # Cuộn xuống cuối trang để tải tất cả nội dung động
            self.scroll_to_bottom()

            # Đợi tài nguyên quan trọng được tải (nếu cần)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'body'))
            )

            return self.driver.page_source  # Trả về HTML của trang
        except Exception as e:
            self.log_error(url, str(e))
            return None

    def save_resource(self, url, content):
        """Lưu HTML của trang web vào tệp"""
        try:
            parsed_url = urlparse(url)
            path = os.path.join(
                self.output_dir,
                parsed_url.netloc,
                parsed_url.path.lstrip('/').replace('/', os.sep)
            )

            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(os.path.dirname(path), exist_ok=True)

            # Nếu không có tên tệp, đặt là index.html
            if path.endswith('/') or not os.path.splitext(path)[1]:
                path = os.path.join(path, 'index.html')

            # Lưu tệp
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.downloaded_files.add(path)
            return path
        except Exception as e:
            self.logger.error(f"Lỗi lưu tài nguyên {url}: {e}")
            return None

    def extract_links(self, html, base_url):
        """Trích xuất liên kết từ HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        links = set()

        # Trích xuất các liên kết <a>
        for a_tag in soup.find_all('a', href=True):
            link = urljoin(base_url, a_tag['href'])
            if link.startswith(self.base_url):  # Chỉ lấy liên kết trong cùng domain
                links.add(link)

        return links

    def crawl(self, url, depth=0):
        """Duyệt và tải nội dung từ URL"""
        if url in self.visited_urls or depth > self.max_depth:
            return

        self.visited_urls.add(url)
        self.logger.info(f"Đang duyệt: {url}")

        # Tải trang và lưu nội dung
        html = self.fetch_page(url)
        if html:
            self.save_resource(url, html)

            # Trích xuất liên kết và tiếp tục duyệt
            links = self.extract_links(html, url)
            for link in links:
                self.crawl(link, depth + 1)

    def run(self):
        """Chạy toàn bộ quá trình"""
        self.logger.info(f"Bắt đầu cào trang {self.base_url}")
        self.crawl(self.base_url)
        self.logger.info("Hoàn tất việc tải tất cả nội dung.")
        self.driver.quit()


if __name__ == '__main__':
    base_url = input("Nhập URL trang web cần cào: ").strip()
    output_dir = input("Nhập tên thư mục lưu kết quả (mặc định: cloned_site): ").strip() or 'cloned_site'
    max_depth = int(input("Nhập độ sâu tối đa để cào (mặc định: 5): ") or 5)

    downloader = WebsiteDownloaderWithScroll(base_url, output_dir, max_depth)
    downloader.run()
