import os
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import time
from random import randint

# Đọc các URL từ file output.txt
def read_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Kiểm tra xem chuỗi có phải là URL hợp lệ hay không
def is_valid_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme in ['http', 'https'] and parsed_url.netloc != ''

# Tải một trang web và lưu vào tệp .html trong thư mục error_site theo cấu trúc URL
def download_site(url, base_folder, retries=3, delay=2):
    try:
        if not is_valid_url(url):
            print(f"Không phải URL hợp lệ: {url}")
            return

        # Gửi yêu cầu GET để tải nội dung trang web
        response = requests.get(url)
        
        # Kiểm tra lỗi 429 (Too Many Requests)
        if response.status_code == 429:
            print(f"Đã gặp lỗi 429 (Too Many Requests) cho {url}. Thử lại sau {delay} giây.")
            time.sleep(delay)  # Chờ một thời gian trước khi thử lại
            return download_site(url, base_folder, retries-1, delay * 2)  # Tăng thời gian chờ và thử lại nếu còn retries

        response.raise_for_status()  # Kiểm tra xem yêu cầu có thành công không (lỗi khác sẽ được raise)

        # Phân tách domain và path từ URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('www.', '')  # Loại bỏ 'www.'
        path = parsed_url.path.strip('/')

        # Tạo cấu trúc thư mục từ domain và path
        path_parts = path.split('/')
        directory = os.path.join(base_folder, domain, *path_parts[:-1])

        # Tạo thư mục nếu chưa có
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Tạo tên file từ phần cuối cùng của URL
        filename = path_parts[-1] if path_parts[-1] else 'index'
        filename = filename + '.html'

        # Đường dẫn lưu file
        file_path = os.path.join(directory, filename)

        # Lưu nội dung trang web vào tệp .html
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        print(f"Đã tải xuống: {url} vào {file_path}")

    except requests.exceptions.RequestException as e:
        print(f"Không thể tải xuống {url}: {e}")
    except Exception as e:
        print(f"Đã gặp lỗi trong quá trình tải trang {url}: {e}")

# Main function để tải nhiều trang web song song
def main():
    file_path = 'output.txt'  # Đường dẫn đến file chứa các URL
    base_folder = 'error_site'  # Thư mục gốc 'error_site'

    # Đọc các URL từ file
    urls = read_urls_from_file(file_path)

    # Tải các trang web song song với ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(lambda url: download_site(url, base_folder), urls)

if __name__ == '__main__':
    main()
