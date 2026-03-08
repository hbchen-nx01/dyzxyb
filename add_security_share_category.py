from app import app
from models import db, ArticleCategory

with app.app_context():
    # 检查"安全分享"分类是否已存在
    existing_category = ArticleCategory.query.filter_by(name='安全分享').first()
    if not existing_category:
        # 创建新分类
        new_category = ArticleCategory(
            name='安全分享',
            description='安全知识、安全经验、安全警示等内容分享'
        )
        # 添加到数据库
        db.session.add(new_category)
        db.session.commit()
        print('"安全分享"分类已成功添加到经验分享模块！')
    else:
        print('"安全分享"分类已存在，无需重复添加！')
