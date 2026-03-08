from app import app
from models import db

with app.app_context():
    # 获取数据库连接
    conn = db.engine.raw_connection()
    cursor = conn.cursor()
    
    # 检查equipment表结构
    cursor.execute("PRAGMA table_info(equipment);")
    columns = cursor.fetchall()
    
    print("Equipment表结构:")
    print("ID	名称	类型	是否可以为空	默认值	主键")
    for column in columns:
        print(f"{column[0]}	{column[1]}	{column[2]}	{column[3]}	{column[4]}	{column[5]}")
    
    # 检查equipment_category表是否存在
    try:
        cursor.execute("PRAGMA table_info(equipment_category);")
        category_columns = cursor.fetchall()
        print("\nEquipment_category表结构:")
        print("ID	名称	类型	是否可以为空	默认值	主键")
        for column in category_columns:
            print(f"{column[0]}	{column[1]}	{column[2]}	{column[3]}	{column[4]}	{column[5]}")
    except Exception as e:
        print(f"\nEquipment_category表不存在或无法访问: {e}")
    
    cursor.close()
    conn.close()