import requests
import os

# 服务器地址
BASE_URL = 'http://127.0.0.1:5001'

# 1. 先获取当前设备数量
equipment_list_url = f'{BASE_URL}/maintenance/equipment/'
response = requests.get(equipment_list_url)
print(f'当前设备列表页面响应状态码: {response.status_code}')

# 2. 上传测试Excel文件
import_url = f'{BASE_URL}/maintenance/equipment/import/'
file_path = 'test_equipment.xlsx'

if os.path.exists(file_path):
    files = {'file': open(file_path, 'rb')}
    response = requests.post(import_url, files=files)
    print(f'导入请求响应状态码: {response.status_code}')
    print(f'导入请求响应内容: {response.text[:500]}...')
    print('\n导入测试完成！')
else:
    print(f'测试文件 {file_path} 不存在')