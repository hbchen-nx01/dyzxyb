import requests
import os
from bs4 import BeautifulSoup

# 服务器地址
BASE_URL = 'http://127.0.0.1:5001'

# 1. 先获取导入页面，获取CSRF令牌（如果需要）
import_page_url = f'{BASE_URL}/maintenance/equipment/import/'
response = requests.get(import_page_url)
print(f'导入页面响应状态码: {response.status_code}')

# 解析HTML获取CSRF令牌
soup = BeautifulSoup(response.text, 'html.parser')
csrf_token = None
meta_tag = soup.find('meta', attrs={'name': 'csrf-token'})
if meta_tag:
    csrf_token = meta_tag.get('content')
    print(f'CSRF令牌: {csrf_token}')

# 2. 上传测试Excel文件
import_url = f'{BASE_URL}/maintenance/equipment/import/'
file_path = 'test_equipment.xlsx'

if os.path.exists(file_path):
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # 添加CSRF令牌到请求头
    if csrf_token:
        headers['X-CSRF-Token'] = csrf_token
    
    # 准备文件
    files = {
        'file': (file_path, open(file_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    }
    
    # 发送POST请求
    print(f'正在上传文件: {file_path}')
    response = requests.post(import_url, files=files, headers=headers, allow_redirects=False)
    
    print(f'导入请求响应状态码: {response.status_code}')
    print(f'响应头: {response.headers}')
    
    # 检查是否重定向
    if response.status_code in [301, 302]:
        redirect_url = response.headers.get('Location')
        print(f'重定向到: {redirect_url}')
        
        # 跟随重定向
        if redirect_url.startswith('http'):
            response = requests.get(redirect_url)
        else:
            response = requests.get(f'{BASE_URL}{redirect_url}')
        print(f'重定向后响应状态码: {response.status_code}')
    
    # 检查响应内容中的flash消息
    soup = BeautifulSoup(response.text, 'html.parser')
    flash_messages = soup.find_all('div', class_=['alert', 'flash'])
    if flash_messages:
        print('\nFlash消息:')
        for msg in flash_messages:
            print(f'- {msg.text.strip()}')
    else:
        print('\n未找到Flash消息')
    
    print('\n导入测试完成！')
else:
    print(f'测试文件 {file_path} 不存在')