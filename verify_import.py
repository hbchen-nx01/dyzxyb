from app import app
from models import db, Equipment

# 初始化应用上下文
with app.app_context():
    print("验证数据库导入结果...")
    
    # 获取所有导入的设备
    equipments = Equipment.query.all()
    
    print(f"\n共导入 {len(equipments)} 条设备记录：")
    print("=" * 100)
    
    # 打印设备详情
    for i, equipment in enumerate(equipments, 1):
        print(f"\n设备 {i}:")
        print(f"  设备位号: {equipment.equipment_number}")
        print(f"  设备名称: {equipment.name}")
        print(f"  设备型号: {equipment.model}")
        print(f"  规格: {equipment.specification}")
        print(f"  设备序列号: {equipment.serial_number}")
        print(f"  安装位置: {equipment.location}")
        print(f"  使用部门: {equipment.department}")
        print(f"  责任人: {equipment.responsible_person}")
        print(f"  联系方式: {equipment.phone}")
        print(f"  采购日期: {equipment.purchase_date}")
        print(f"  采购价格: {equipment.purchase_price}")
        print(f"  制造商: {equipment.manufacturer}")
        print(f"  供应商: {equipment.supplier}")
        print(f"  保修期限: {equipment.warranty_period}")
        print(f"  设备状态: {equipment.status}")
        print(f"  最近维护日期: {equipment.last_maintenance_date}")
        print(f"  下次维护日期: {equipment.next_maintenance_date}")
        print(f"  维护时间间隔: {equipment.maintenance_interval}")
        print(f"  设备描述: {equipment.description}")
        print(f"  创建时间: {equipment.created_at}")
    
    print("\n" + "=" * 100)
    print("验证完成！")
