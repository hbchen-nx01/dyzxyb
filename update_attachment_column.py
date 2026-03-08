from app import app
from models import db, LeaveApplication

with app.app_context():
    # 检查数据库中是否已经有attachment列
    inspector = db.inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('leave_application')]
    
    if 'attachment' not in columns:
        # 使用SQL语句添加attachment列
        with db.engine.connect() as conn:
            conn.execute(db.text('ALTER TABLE leave_application ADD COLUMN attachment VARCHAR(255)'))
            conn.commit()
        print("已成功添加attachment列")
    else:
        print("attachment列已存在")
