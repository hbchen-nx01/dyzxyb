from app import app, db
from models import Employee

with app.app_context():
    try:
        # 查询所有员工
        print('查询所有员工...')
        employees = Employee.query.all()
        print(f'员工总数：{len(employees)}')
        
        for emp in employees:
            print(f'员工ID：{emp.id}，姓名：{emp.name}，编号：{emp.employee_id}')
            
            # 直接访问资格证书关系，测试是否有错误
            print(f'  资格证书数量：{len(emp.qualification_certificates)}')
            
            # 直接访问技能等级关系，测试是否有错误
            print(f'  技能数量：{len(emp.skill_levels)}')
            
            # 直接访问培训经历关系，测试是否有错误
            print(f'  培训经历数量：{len(emp.training_experiences)}')
        
        print('所有关系访问成功！')
        
    except Exception as e:
        print(f'发生错误：{type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()