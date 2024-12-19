import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import random
import logging


class OptimizedWebsiteDownloader:
    def __init__(self, base_url, output_dir='cloned_site', max_depth=5):
        self.base_url = base_url.rstrip('/')
        self.output_dir = output_dir
        self.max_depth = max_depth
        self.visited_urls = set()
        self.downloaded_files = set()
        self.session = requests.Session()
        
        # Danh sách User-Agent để tránh bị chặn
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
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
            'DNT': '1',
            'Connection': 'keep-alive'
        }

    def save_resource(self, url, content, is_binary=False):
        """Lưu tài nguyên vào thư mục"""
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
            if is_binary:
                with open(path, 'wb') as f:
                    f.write(content)
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

            self.downloaded_files.add(path)
            return path
        except Exception as e:
            self.logger.error(f"Lỗi lưu tài nguyên {url}: {e}")
            return None

    def extract_links_and_assets(self, html, base_url):
        """Trích xuất liên kết và tài nguyên từ HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        assets = set()

        # Trích xuất các URL trong <a>, <link>, <img>, <script>, <source>, v.v.
        for attr, tag in [
            ('href', ['a', 'link']),
            ('src', ['img', 'script', 'source'])
        ]:
            for element in soup.find_all(tag):
                url = element.get(attr)
                if url:
                    full_url = urljoin(base_url, url)
                    if full_url.startswith(self.base_url):
                        if tag == 'a':
                            links.add(full_url)  # Liên kết HTML
                        else:
                            assets.add(full_url)  # Tài nguyên (CSS, JS, ảnh)

        # Loại bỏ iframe
        for iframe in soup.find_all('iframe'):
            iframe_src = iframe.get('src')
            if iframe_src:
                full_url = urljoin(base_url, iframe_src)
                links.discard(full_url)

        return links, assets

    def fetch_url(self, url):
        """Tải nội dung từ URL"""
        try:
            response = self.session.get(
                url, headers=self.get_random_headers(), timeout=10
            )
            if response.status_code == 200:
                return response
            else:
                self.log_error(url, f"Status code {response.status_code}")
                return None
        except Exception as e:
            self.log_error(url, str(e))
            return None

    def download_assets(self, assets):
        """Tải và lưu tất cả tài nguyên (CSS, JS, ảnh, v.v.)"""
        for asset in assets:
            if asset in self.visited_urls:
                continue  # Bỏ qua nếu đã tải
            self.visited_urls.add(asset)

            try:
                response = self.fetch_url(asset)
                if response and response.status_code == 200:
                    self.save_resource(asset, response.content, is_binary=True)
                else:
                    self.log_error(asset, f"Không thể tải tài nguyên.")
            except Exception as e:
                self.log_error(asset, str(e))

    def crawl(self, url, depth=0):
        """Duyệt và tải nội dung từ URL"""
        if url in self.visited_urls or depth > self.max_depth:
            return

        self.visited_urls.add(url)
        self.logger.info(f"Đang tải: {url}")

        response = self.fetch_url(url)
        if response and response.status_code == 200:
            html = response.text
            self.save_resource(url, html)

            links, assets = self.extract_links_and_assets(html, url)
            self.download_assets(assets)

            for link in links:
                self.crawl(link, depth + 1)

    def run(self):
        """Chạy toàn bộ quá trình"""
        self.logger.info(f"Bắt đầu cào trang {self.base_url}")
        self.crawl(self.base_url)
        self.logger.info("Hoàn tất việc tải tất cả nội dung.")


if __name__ == '__main__':
    base_url = input("Nhập URL trang web cần cào: ").strip()
    output_dir = input("Nhập tên thư mục lưu kết quả (mặc định: cloned_site): ").strip() or 'cloned_site'
    max_depth = int(input("Nhập độ sâu tối đa để cào (mặc định: 5): ") or 5)

    downloader = OptimizedWebsiteDownloader(base_url, output_dir, max_depth)
    downloader.run()
