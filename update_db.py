from app import app, db
import sqlite3

with app.app_context():
    # 直接使用SQLite连接来添加字段
    conn = sqlite3.connect('instance/employee_management.db')
    cursor = conn.cursor()
    
    try:
        # 添加file_path字段
        cursor.execute("ALTER TABLE qualification_certificate ADD COLUMN file_path TEXT")
        conn.commit()
        print("成功添加file_path字段到qualification_certificate表")
    except sqlite3.OperationalError as e:
        print(f"错误：{e}")
        if "duplicate column name" in str(e):
            print("file_path字段已经存在")
    finally:
        conn.close()