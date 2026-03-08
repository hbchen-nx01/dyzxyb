from app import app, db
from models import Employee
from datetime import datetime

# 使用应用上下文
with app.app_context():
    # 创建一个员工记录
    new_employee = Employee(
        employee_id='EMP001',
        name='张三',
        gender='男',
        birthday=datetime.strptime('1990-01-01', '%Y-%m-%d').date(),
        position='设备维修员',
        contact='13800138000',
        education='大专',
        school='职业技术学院'
    )
    
    # 保存到数据库
    db.session.add(new_employee)
    db.session.commit()
    
    print(f'成功添加员工：{new_employee.name} (ID: {new_employee.id})')