import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import random
import time
import logging


class OptimizedWebsiteCrawler:
    def __init__(self, base_url, output_dir='cloned_site', max_depth=5, max_workers=10):
        self.base_url = base_url.rstrip('/')
        self.output_dir = output_dir
        self.max_depth = max_depth
        self.visited_urls = set()
        self.collected_urls = set()
        self.session = requests.Session()
        self.max_workers = max_workers

        # Danh sách User-Agent để luân chuyển
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]

        # Cấu hình logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Tệp log lỗi
        self.error_log_file = os.path.join(self.output_dir, "error_log.txt")
        os.makedirs(self.output_dir, exist_ok=True)

        # Khởi tạo file log lỗi
        with open(self.error_log_file, 'w', encoding='utf-8') as f:
            f.write("=== Error Log ===\n")

    def log_error(self, url, error_message):
        """Ghi lỗi vào tệp log"""
        with open(self.error_log_file, 'a', encoding='utf-8') as f:
            f.write(f"{url} - Error: {error_message}\n")
        self.logger.error(f"Lỗi {url}: {error_message}")

    def get_random_headers(self):
        """Tạo headers ngẫu nhiên để tránh bị chặn"""
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
        """Lưu tài nguyên vào đĩa"""
        try:
            parsed_url = urlparse(url)
            path = os.path.join(
                self.output_dir,
                parsed_url.netloc,
                parsed_url.path.lstrip('/').replace('/', os.sep)
            )

            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(os.path.dirname(path), exist_ok=True)

            # Xử lý tên tệp mặc định
            if path.endswith('/') or not os.path.splitext(path)[1]:
                path = os.path.join(path, 'index.html')

            # Ghi file
            if is_binary:
                with open(path, 'wb') as f:
                    f.write(content)
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

            return path
        except Exception as e:
            self.logger.error(f"Lỗi lưu tài nguyên {url}: {e}")
            return None

    def extract_links(self, html, base_url):
        """Trích xuất các liên kết từ HTML, loại trừ iframe"""
        soup = BeautifulSoup(html, 'html.parser')
        links = set()

        # Trích xuất liên kết từ các thẻ <a>, <link>, <script>, <img>
        for attr, tag in [
            ('href', ['a', 'link']),
            ('src', ['img', 'script', 'source'])
        ]:
            for element in soup.find_all(tag):
                link = element.get(attr)
                if link:
                    full_url = urljoin(base_url, link)
                    if full_url.startswith(self.base_url):
                        links.add(full_url)

        # Loại bỏ các URL xuất hiện trong iframe
        for iframe in soup.find_all('iframe'):
            iframe_src = iframe.get('src')
            if iframe_src:
                full_url = urljoin(base_url, iframe_src)
                links.discard(full_url)

        return links

    def fetch_and_collect_links(self, url, depth=0):
        """Tải trang và thu thập các liên kết"""
        try:
            if url in self.visited_urls or depth > self.max_depth:
                return

            response = self.session.get(
                url, headers=self.get_random_headers(), timeout=10
            )
            if response.status_code != 200:
                self.log_error(url, f"Status code {response.status_code}")
                return

            self.visited_urls.add(url)
            html = response.text
            self.save_resource(url, html)

            links = self.extract_links(html, url)
            for link in links:
                if link not in self.collected_urls:
                    self.collected_urls.add(link)

            # Nghỉ ngắn để tránh bị chặn
            time.sleep(random.uniform(0.5, 1.5))
        except Exception as e:
            self.log_error(url, str(e))

    def collect_all_links(self):
        """Duyệt toàn bộ trang và thu thập tất cả liên kết"""
        self.logger.info("Đang thu thập toàn bộ liên kết...")
        urls_to_visit = {self.base_url}

        while urls_to_visit:
            url = urls_to_visit.pop()
            self.fetch_and_collect_links(url)
            urls_to_visit.update(self.collected_urls - self.visited_urls)

    def download_all(self):
        """Tải tất cả liên kết đã thu thập"""
        self.logger.info("Bắt đầu tải xuống tất cả các trang...")
        for url in self.collected_urls:
            try:
                response = self.session.get(url, headers=self.get_random_headers(), timeout=10)
                if response.status_code == 200:
                    self.save_resource(url, response.content, is_binary=True)
                else:
                    self.log_error(url, f"Status code {response.status_code}")
            except Exception as e:
                self.log_error(url, str(e))

    def run(self):
        """Chạy quá trình thu thập và tải xuống"""
        self.collect_all_links()
        self.download_all()
        self.logger.info("Hoàn tất việc tải xuống tất cả trang.")


if __name__ == '__main__':
    base_url = input("Nhập URL trang web cần cào: ").strip()
    crawler = OptimizedWebsiteCrawler(base_url)
    crawler.run()
