from app import app
from models import db, EquipmentCategory

# 初始化应用上下文
with app.app_context():
    print("当前设备分类列表：")
    
    # 查询所有设备分类
    current_categories = EquipmentCategory.query.all()
    
    if not current_categories:
        print("数据库中没有设备分类，将创建新的分类。")
    else:
        print("现有分类：")
        for category in current_categories:
            parent_name = category.parent.name if category.parent else '无'
            print(f"  ID: {category.id}, 名称: {category.name}, 父分类: {parent_name}, 描述: {category.description}")
    
    # 要创建的设备分类
    required_categories = [
        "阀门",
        "流量计",
        "温度",
        "压力",
        "液位",
        "分析",
        "检测器",
        "环保"
    ]
    
    print("\n开始更新设备分类...")
    
    # 创建或更新设备分类
    for category_name in required_categories:
        # 检查分类是否已存在
        existing_category = EquipmentCategory.query.filter_by(name=category_name).first()
        
        if existing_category:
            print(f"  分类 '{category_name}' 已存在，跳过。")
        else:
            # 创建新分类
            new_category = EquipmentCategory(
                name=category_name,
                parent_id=None,  # 创建为顶级分类
                description=f"{category_name}设备分类"
            )
            
            db.session.add(new_category)
            print(f"  创建新分类: {category_name}")
    
    # 提交更改
    try:
        db.session.commit()
        print("\n设备分类更新成功！")
        
        # 显示更新后的分类
        print("\n更新后的设备分类列表：")
        updated_categories = EquipmentCategory.query.all()
        for category in updated_categories:
            parent_name = category.parent.name if category.parent else '无'
            print(f"  ID: {category.id}, 名称: {category.name}, 父分类: {parent_name}, 描述: {category.description}")
            
    except Exception as e:
        db.session.rollback()
        print(f"\n更新失败：{e}")
