import requests

try:
    # 测试员工列表页面
    response = requests.get('http://127.0.0.1:5001/employee/')
    print(f'员工列表页面状态码: {response.status_code}')
    if response.status_code == 200:
        print('员工列表页面访问成功！')
        print(f'页面内容长度: {len(response.text)} 字符')
        print('页面内容前100个字符:')
        print(response.text[:100])
    else:
        print(f'员工列表页面访问失败: {response.status_code}')
        print(f'响应内容: {response.text}')
    
    # 测试员工详情页面（假设存在ID为1的员工）
    response_detail = requests.get('http://127.0.0.1:5001/employee/detail/1')
    print(f'\n员工详情页面状态码: {response_detail.status_code}')
    if response_detail.status_code == 200:
        print('员工详情页面访问成功！')
        print(f'页面内容长度: {len(response_detail.text)} 字符')
        print('页面内容前200个字符:')
        print(response_detail.text[:200])
    else:
        print(f'员工详情页面访问失败: {response_detail.status_code}')
        print(f'响应内容: {response_detail.text}')
        
except Exception as e:
    print(f'发生错误: {type(e).__name__}: {e}')
