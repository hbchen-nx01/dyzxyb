from models import db, DocumentCategory
from app import app

# 创建应用上下文
with app.app_context():
    # 定义需要添加的分类结构
    categories_to_add = {
        '班组管理类': {
            'description': '班组管理相关文档',
            'children': ['排班表', '考勤记录', '绩效方案', '会议纪要']
        },
        '设备台账类': {
            'description': '设备台账相关文档',
            'children': ['仪表型号清单', '校准记录', '故障历史台账']
        },
        '维修技术类': {
            'description': '维修技术相关文档',
            'children': ['维修手册', '故障排查流程', '备件更换指导']
        },
        '安全合规类': {
            'description': '安全合规相关文档',
            'children': ['作业票证模板', '安全操作规程', '应急处置方案']
        },
        '培训资料类': {
            'description': '培训资料相关文档',
            'children': ['新人培训课件', '技能考核题库', '案例分析文档']
        }
    }
    
    # 遍历分类结构并添加到数据库
    for category_name, category_info in categories_to_add.items():
        # 检查父分类是否存在
        parent_category = DocumentCategory.query.filter_by(name=category_name).first()
        
        if not parent_category:
            # 创建父分类
            parent_category = DocumentCategory(
                name=category_name,
                description=category_info['description']
            )
            db.session.add(parent_category)
            db.session.commit()
            print(f'已创建父分类: {category_name}')
        
        # 添加子分类
        for child_name in category_info['children']:
            # 检查子分类是否存在
            child_category = DocumentCategory.query.filter_by(name=child_name, parent_id=parent_category.id).first()
            
            if not child_category:
                # 创建子分类
                child_category = DocumentCategory(
                    name=child_name,
                    parent_id=parent_category.id,
                    description=f'{category_name} - {child_name}'
                )
                db.session.add(child_category)
                db.session.commit()
                print(f'  已创建子分类: {child_name}')
    
    print('\n文档分类添加完成！')
    
    # 打印所有分类（用于验证）
    print('\n当前所有文档分类：')
    all_categories = DocumentCategory.query.order_by(DocumentCategory.parent_id, DocumentCategory.name).all()
    for category in all_categories:
        if category.parent_id:
            print(f'  └─ {category.name} (父分类: {category.parent.name})')
        else:
            print(f'{category.name}')
