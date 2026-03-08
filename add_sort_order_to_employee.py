from app import app
from models import db, Employee

with app.app_context():
    # 检查是否已经有sort_order列
    with db.engine.connect() as conn:
        result = conn.execute(db.text("PRAGMA table_info(employee)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'sort_order' not in columns:
            # 添加sort_order列
            conn.execute(db.text("ALTER TABLE employee ADD COLUMN sort_order INTEGER DEFAULT 0"))
            print("添加sort_order列成功")
        else:
            print("sort_order列已存在")
    
    # 初始化sort_order值
    employees = Employee.query.order_by(Employee.id).all()
    for index, employee in enumerate(employees):
        employee.sort_order = index
    
    db.session.commit()
    print("初始化sort_order值成功")
