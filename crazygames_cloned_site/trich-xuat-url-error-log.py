import re

# Đường dẫn đến file .txt
file_path = 'error_log.txt'  # Thay bằng tên file của bạn
output_path = 'output.txt'  # Tên file kết quả

# Biểu thức regex để tìm URL
regex = r'https://www\.crazygames\.com[^\s"\'<>]*'

# Đọc nội dung file
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Tìm tất cả URL phù hợp
urls = re.findall(regex, content)

# Ghi kết quả vào file mới
with open(output_path, 'w', encoding='utf-8') as output_file:
    output_file.write('\n'.join(urls))

print(f"Trích xuất xong! URL được lưu tại: {output_path}")
