import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.abspath('.'))

from app import app, db
from models import Equipment

with app.app_context():
    # 查询所有设备
    equipments = Equipment.query.all()
    print(f'数据库中共有 {len(equipments)} 条设备记录')
    
    # 打印设备信息
    for equipment in equipments:
        print(f'设备位号: {equipment.equipment_number}, 设备名称: {equipment.name}, 状态: {equipment.status}')
    
    # 检查测试数据是否存在
    test_equipment = Equipment.query.filter_by(equipment_number='EQ001').first()
    if test_equipment:
        print('\n测试数据 EQ001 导入成功！')
    else:
        print('\n测试数据 EQ001 导入失败！')