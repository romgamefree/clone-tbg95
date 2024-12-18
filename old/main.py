import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import concurrent.futures
import random
import time
import logging

class WebsiteCrawler:
    def __init__(self, base_url, output_dir='cloned_site', max_depth=5):
        self.base_url = base_url.rstrip('/')
        self.output_dir = output_dir
        self.max_depth = max_depth
        self.visited_urls = set()
        self.session = requests.Session()
        
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
                with open(path, 'wb') as f:  # No encoding specified for binary mode
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
        
        # Trích xuất liên kết từ các thẻ <a> và <link> (có thể có href)
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
        
        return links

    def download_resource(self, url):
        """Tải xuống tài nguyên"""
        try:
            response = self.session.get(
                url, 
                headers=self.get_random_headers(), 
                timeout=10
            )
            
            if response.status_code == 200:
                # Nếu không phải HTML
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' not in content_type:
                    self.save_resource(url, response.content, is_binary=True)
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Lỗi tải tài nguyên {url}: {e}")
            return False

    def clone_website(self):
        """Quá trình clone website chính"""
        # Tạo thư mục đầu ra
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Danh sách URL để duyệt
        urls_to_visit = {self.base_url}
        visited_depth = {self.base_url: 0}
        
        while urls_to_visit:
            url = urls_to_visit.pop()
            
            # Bỏ qua nếu đã duyệt hoặc vượt độ sâu
            if url in self.visited_urls or visited_depth.get(url, 0) > self.max_depth:
                continue
            
            self.logger.info(f"Đang clone: {url}")
            
            try:
                # Tải trang với headers ngẫu nhiên
                response = self.session.get(
                    url, 
                    headers=self.get_random_headers(), 
                    timeout=10
                )
                
                if response.status_code != 200:
                    self.logger.warning(f"Không thể tải {url}: Mã trạng thái {response.status_code}")
                    continue
                
                # Lưu trang HTML
                html = response.text
                self.save_resource(url, html)
                self.visited_urls.add(url)
                
                # Trích xuất và lập lịch các liên kết
                links = self.extract_links(html, url)
                for link in links:
                    if link not in self.visited_urls:
                        urls_to_visit.add(link)
                        visited_depth[link] = visited_depth.get(url, 0) + 1
                
                # Tải xuống tài nguyên đính kèm
                resources = [
                    link for link in links 
                    if any(link.endswith(ext) for ext in ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf'])
                ]
                
                # Tải xuống song song các tài nguyên
                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    executor.map(self.download_resource, resources)
                
                # Nghỉ ngơi ngắn để tránh quá tải
                time.sleep(random.uniform(0.5, 2))
            
            except Exception as e:
                self.logger.error(f"Lỗi khi clone {url}: {e}")
        
        print("Hoàn tất clone website!")

def main():
    base_url = 'https://tbg95.github.io/'
    cloner = WebsiteCrawler(base_url, max_depth=10)
    cloner.clone_website()

if __name__ == '__main__':
    main()
