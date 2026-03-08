#!/usr/bin/env python3
"""
数据库迁移脚本：将SQLite数据库迁移到外部数据库（如PostgreSQL）
使用方法：
1. 确保已安装所需依赖：pip install sqlalchemy pandas
2. 配置环境变量DATABASE_URL指向目标数据库
3. 运行脚本：python migrate_to_external_db.py
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 加载环境变量
load_dotenv()

def migrate_database():
    """执行数据库迁移"""
    # 获取当前SQLite数据库URL
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    sqlite_url = f'sqlite:///{os.path.join(BASE_DIR, "app.db")}'
    
    # 获取目标数据库URL（从环境变量）
    target_url = os.environ.get('DATABASE_URL')
    if not target_url:
        print("错误：未设置DATABASE_URL环境变量")
        return False
    
    # 确保PostgreSQL URL格式正确
    if target_url.startswith('postgres://'):
        target_url = target_url.replace('postgres://', 'postgresql://')
    
    print(f"迁移源数据库: {sqlite_url}")
    print(f"迁移目标数据库: {target_url}")
    
    try:
        # 创建源数据库引擎和会话
        source_engine = create_engine(sqlite_url, echo=False)
        source_metadata = MetaData(bind=source_engine)
        source_metadata.reflect()
        
        # 创建目标数据库引擎和会话
        target_engine = create_engine(target_url, echo=False)
        target_metadata = MetaData(bind=target_engine)
        
        # 从源数据库反射表结构到目标数据库
        for table_name, table in source_metadata.tables.items():
            print(f"迁移表: {table_name}")
            # 复制表结构
            table.create(bind=target_engine)
            
            # 获取源数据
            source_session = sessionmaker(bind=source_engine)()
            rows = source_session.query(table).all()
            source_session.close()
            
            if rows:
                # 插入数据到目标表
                target_connection = target_engine.connect()
                target_table = Table(table_name, target_metadata, autoload_with=target_engine)
                target_connection.execute(target_table.insert(), [dict(row._asdict()) for row in rows])
                target_connection.commit()
                target_connection.close()
                print(f"  已迁移 {len(rows)} 条记录")
            else:
                print(f"  表为空，无需迁移数据")
        
        print("数据库迁移完成！")
        return True
        
    except Exception as e:
        print(f"迁移过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)