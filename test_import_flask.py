from app import app
from models import db, Equipment
import pytest
import os
from io import BytesIO

# 初始化应用上下文
with app.app_context():
    # 测试Excel导入功能
    def test_excel_import():
        # 创建测试客户端
        client = app.test_client()
        
        # 读取测试Excel文件
        file_path = 'test_equipment.xlsx'
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # 创建表单数据
        data = {
            'file': (BytesIO(file_content), file_path)
        }
        
        print("正在测试Excel导入功能...")
        
        # 发送POST请求
        response = client.post('/maintenance/equipment/import/', data=data, content_type='multipart/form-data', follow_redirects=True)
        
        print(f"请求状态码: {response.status_code}")
        print(f"响应数据: {response.data.decode('utf-8')[:500]}...")  # 只显示前500个字符
        
        # 检查数据库中的设备数量
        equipment_count = Equipment.query.count()
        print(f"导入后数据库中的设备数量: {equipment_count}")
        
        if equipment_count > 0:
            print("导入的设备列表:")
            equipments = Equipment.query.all()
            for equipment in equipments:
                print(f"  - {equipment.equipment_number}: {equipment.name} ({equipment.status})")
            return True
        else:
            print("导入失败，数据库中没有设备")
            return False
    
    # 运行测试
    if __name__ == "__main__":
        test_excel_import()