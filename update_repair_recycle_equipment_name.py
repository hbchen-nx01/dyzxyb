from app import app
from models import db
from sqlalchemy import text

with app.app_context():
    # 检查repair_recycle表是否已经有equipment_name字段
    inspector = db.inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('repair_recycle')]
    
    if 'equipment_name' not in columns:
        # 如果没有，添加该字段
        try:
            with db.engine.connect() as conn:
                # 首先添加字段，允许为空
                conn.execute(text('ALTER TABLE repair_recycle ADD COLUMN equipment_name VARCHAR(200)'))
                # 然后更新现有记录，将设备名称从equipment表同步过来
                conn.execute(text("""
                    UPDATE repair_recycle 
                    SET equipment_name = (SELECT name FROM equipment WHERE id = repair_recycle.equipment_id)
                    WHERE equipment_id IS NOT NULL
                """))
                # 最后将字段设置为非空
                conn.execute(text('ALTER TABLE repair_recycle ALTER COLUMN equipment_name SET NOT NULL'))
                conn.commit()
            print("成功为repair_recycle表添加equipment_name字段并同步数据")
        except Exception as e:
            print(f"添加字段或同步数据时出错: {e}")
    else:
        print("equipment_name字段已经存在于repair_recycle表中")
    
    # 将equipment_id字段设置为允许为空
    if 'equipment_id' in columns:
        column_info = next(col for col in inspector.get_columns('repair_recycle') if col['name'] == 'equipment_id')
        if not column_info['nullable']:
            try:
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE repair_recycle ALTER COLUMN equipment_id DROP NOT NULL'))
                    conn.commit()
                print("成功将repair_recycle表的equipment_id字段设置为允许为空")
            except Exception as e:
                print(f"修改equipment_id字段时出错: {e}")
        else:
            print("equipment_id字段已经允许为空")
