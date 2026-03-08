from app import app
from models import db, Equipment, MaintenanceRecord
import sqlite3

# 使用SQLite直接执行ALTER TABLE语句来添加缺失的列
with app.app_context():
    # 获取数据库连接
    conn = db.engine.raw_connection()
    cursor = conn.cursor()
    
    # 定义要添加的列
    columns_to_add = [
        ("equipment_number", "VARCHAR(100)", "设备位号"),
        ("specification", "VARCHAR(200)", "规格"),
        ("category_id", "INTEGER", "设备分类ID"),
        ("department", "VARCHAR(100)", "使用部门"),
        ("responsible_person", "VARCHAR(100)", "责任人"),
        ("phone", "VARCHAR(20)", "联系方式"),
        ("last_maintenance_date", "DATE", "本次维护日期"),
        ("next_maintenance_date", "DATE", "下次维护日期"),
        ("maintenance_interval", "INTEGER", "维护时间间隔（天）"),
        # 设备状态
        ("status", "VARCHAR(20)", "设备状态"),
        # 采购信息
        ("purchase_date", "DATE", "采购日期"),
        ("purchase_price", "FLOAT", "采购价格（元）"),
        ("manufacturer", "VARCHAR(200)", "制造商"),
        ("supplier", "VARCHAR(200)", "供应商"),
        ("warranty_period", "INTEGER", "保修期（月）"),
        # 报废信息
        ("scrap_date", "DATE", "报废日期"),
        ("scrap_reason", "TEXT", "报废原因"),
        ("scrap_value", "FLOAT", "报废价值（元）"),
        # 新增字段
        ("unit_number", "VARCHAR(50)", "单元号"),
        ("equipment_type", "VARCHAR(50)", "设备类型"),
        ("specs_json", "TEXT", "设备特有属性（JSON格式）")
    ]
    
    # 添加列
    for column_name, column_type, column_comment in columns_to_add:
        try:
            # 添加列
            cursor.execute(f"ALTER TABLE equipment ADD COLUMN {column_name} {column_type}")
            print(f"Added column: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column {column_name} already exists")
            else:
                raise
    
    # 为维护记录表添加缺失的列
    maintenance_columns_to_add = [
        ("spare_parts_used", "TEXT", "使用的备件"),
        ("maintenance_cost", "FLOAT", "维护成本（元）")
    ]
    
    for column_name, column_type, column_comment in maintenance_columns_to_add:
        try:
            # 添加列
            cursor.execute(f"ALTER TABLE maintenance_record ADD COLUMN {column_name} {column_type}")
            print(f"Added column to maintenance_record: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column {column_name} already exists in maintenance_record")
            else:
                raise
    
    # 为故障记录表添加缺失的列
    fault_record_columns_to_add = [
        ("impact_level", "VARCHAR(20)", "影响程度"),
        ("urgency_level", "VARCHAR(20)", "紧急程度")
    ]
    
    for column_name, column_type, column_comment in fault_record_columns_to_add:
        try:
            # 添加列
            cursor.execute(f"ALTER TABLE fault_record ADD COLUMN {column_name} {column_type}")
            print(f"Added column to fault_record: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column {column_name} already exists in fault_record")
            else:
                raise
    
    # 为故障解决方案表添加缺失的列
    fault_solution_columns_to_add = [
        ("spare_parts_used", "TEXT", "使用的备件"),
        ("repair_cost", "FLOAT", "维修成本（元）")
    ]
    
    for column_name, column_type, column_comment in fault_solution_columns_to_add:
        try:
            # 添加列
            cursor.execute(f"ALTER TABLE fault_solution ADD COLUMN {column_name} {column_type}")
            print(f"Added column to fault_solution: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column {column_name} already exists in fault_solution")
            else:
                raise
    
    # 提交事务
    conn.commit()
    print("Database migration completed successfully!")
    
    # 关闭连接
    cursor.close()
    conn.close()