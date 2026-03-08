from app import app, db
from models import ArticleCategory

def add_security_category():
    """添加安全分享分类"""
    with app.app_context():
        # 检查分类是否已存在
        existing_category = ArticleCategory.query.filter_by(name='安全分享').first()
        
        if existing_category:
            print("'安全分享'分类已存在！")
            return
        
        # 创建新分类
        security_category = ArticleCategory(
            name='安全分享',
            description='安全操作、事故预防和安全管理相关的分享内容'
        )
        
        # 添加到数据库
        try:
            db.session.add(security_category)
            db.session.commit()
            print("'安全分享'分类添加成功！")
            
            # 显示所有分类
            categories = ArticleCategory.query.all()
            print("\n当前所有文章分类：")
            for category in categories:
                print(f"- {category.name}")
                
        except Exception as e:
            db.session.rollback()
            print(f"添加分类失败：{e}")

if __name__ == '__main__':
    add_security_category()
