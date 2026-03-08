from app import app
from models import db
import sqlite3

# 使用SQLite直接执行ALTER TABLE语句来添加缺失的file_path列
with app.app_context():
    # 获取数据库连接
    conn = db.engine.raw_connection()
    cursor = conn.cursor()
    
    try:
        # 为资质证书表添加file_path列
        cursor.execute("ALTER TABLE qualification_certificate ADD COLUMN file_path VARCHAR(255)")
        print("Added column: qualification_certificate.file_path")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column qualification_certificate.file_path already exists")
        else:
            raise
    
    # 提交事务
    conn.commit()
    print("Database migration completed successfully!")
    
    # 关闭连接
    cursor.close()
    conn.close()
