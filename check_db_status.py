from app import app
from models import db, Equipment

# 初始化应用上下文
with app.app_context():
    # 检查设备数量
    equipment_count = Equipment.query.count()
    print(f"当前数据库中的设备数量: {equipment_count}")
    
    # 如果有设备，显示设备位号
    if equipment_count > 0:
        print("设备位号列表:")
        equipments = Equipment.query.all()
        for equipment in equipments:
            print(f"  - {equipment.equipment_number} ({equipment.name})")