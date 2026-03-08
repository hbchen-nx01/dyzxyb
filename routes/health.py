from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Employee, EmployeeHealthRecord, TeamHealthStats
from datetime import datetime, date, timedelta
import calendar

# 创建情绪与健康模块的Blueprint
health_bp = Blueprint('health', __name__, url_prefix='/health')


@health_bp.route('/')
def health_index():
    """情绪与健康模块首页"""
    # 获取当前月份
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # 获取或创建本月的统计数据
    first_day = date(current_year, current_month, 1)
    last_day = date(current_year, current_month, calendar.monthrange(current_year, current_month)[1])
    
    # 计算本月的统计数据
    total_employees = Employee.query.count()
    
    # 获取当月所有员工的健康记录
    health_records = EmployeeHealthRecord.query.filter(
        db.extract('year', EmployeeHealthRecord.record_date) == current_year,
        db.extract('month', EmployeeHealthRecord.record_date) == current_month
    ).all()
    
    # 统计适合工作和不适合工作的人数
    available_count = len([r for r in health_records if r.work_suitability])
    unavailable_count = len([r for r in health_records if not r.work_suitability])
    
    # 获取最新的员工健康记录
    latest_records = []
    employees = Employee.query.all()
    
    for employee in employees:
        # 获取该员工最新的健康记录
        latest_record = EmployeeHealthRecord.query.filter_by(
            employee_id=employee.id
        ).order_by(EmployeeHealthRecord.record_date.desc()).first()
        
        if latest_record:
            latest_records.append(latest_record)
    
    # 为每个健康记录添加健康等级和颜色信息
    for record in latest_records:
        record.mental_level, record.mental_color = get_health_level(record.mental_state)
        record.physical_level, record.physical_color = get_health_level(record.physical_health)

    return render_template('health/index.html', 
                         current_year=current_year,
                         current_month=current_month,
                         selected_year_month=f"{current_year}-{current_month:02d}",
                         total_count=total_employees,
                         available_count=available_count,
                         unavailable_count=unavailable_count,
                         health_records=latest_records,
                         get_health_level=get_health_level,
                         get_health_color=get_health_color)


def get_health_level(score):
    """根据分数获取健康等级和颜色"""
    if score <= 2:
        return "极差", "danger"
    elif score <= 4:
        return "较差", "warning"
    elif score <= 6:
        return "一般", "info"
    elif score <= 8:
        return "良好", "primary"
    else:
        return "极佳", "success"

def get_health_color(score):
    """根据分数获取健康等级对应的颜色"""
    if score <= 2:
        return "danger"
    elif score <= 4:
        return "warning"
    elif score <= 6:
        return "info"
    elif score <= 8:
        return "primary"
    else:
        return "success"


@health_bp.route('/add_record', methods=['GET', 'POST'])
def add_health_record():
    """添加员工健康记录"""
    if request.method == 'POST':
        try:
            employee_id = request.form['employee_id']
            record_date = datetime.strptime(request.form['record_date'], '%Y-%m-%d').date()
            mental_state = int(request.form['mental_state'])
            physical_health = int(request.form['physical_health'])
            
            # 自动计算工作适配性：情绪状态≤2分或身体健康≤2分时，不适合工作
            work_suitability = not (mental_state <= 2 or physical_health <= 2)
            
            mood_diary = request.form.get('mood_diary')
            
            # 创建新的健康记录
            new_record = EmployeeHealthRecord(
                employee_id=employee_id,
                record_date=record_date,
                mental_state=mental_state,
                physical_health=physical_health,
                work_suitability=work_suitability,
                mood_diary=mood_diary
            )
            
            db.session.add(new_record)
            db.session.commit()
            
            flash('健康记录添加成功', 'success')
            return redirect(url_for('health.health_index'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败: {str(e)}', 'danger')
    
    # GET 请求：显示添加表单
    employees = Employee.query.all()
    return render_template('health/add_record.html', employees=employees, today=date.today())


@health_bp.route('/edit_record/<int:record_id>', methods=['GET', 'POST'])
def edit_health_record(record_id):
    """编辑员工健康记录"""
    record = EmployeeHealthRecord.query.get_or_404(record_id)
    
    if request.method == 'POST':
        try:
            record.mental_state = int(request.form['mental_state'])
            record.physical_health = int(request.form['physical_health'])
            
            # 自动计算工作适配性：情绪状态≤2分或身体健康≤2分时，不适合工作
            record.work_suitability = not (record.mental_state <= 2 or record.physical_health <= 2)
            
            record.mood_diary = request.form.get('mood_diary')
            
            db.session.commit()
            flash('健康记录更新成功', 'success')
            return redirect(url_for('health.health_index'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'danger')
    
    employees = Employee.query.all()
    return render_template('health/edit_record.html', record=record, employees=employees)


@health_bp.route('/delete_record/<int:record_id>')
def delete_health_record(record_id):
    """删除员工健康记录"""
    try:
        record = EmployeeHealthRecord.query.get_or_404(record_id)
        db.session.delete(record)
        db.session.commit()
        flash('健康记录删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'danger')
    
    return redirect(url_for('health.health_index'))


@health_bp.route('/stats/<int:year>/<int:month>')
def health_stats(year, month):
    """查看指定月份的健康统计数据"""
    # 获取当月的统计数据
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    
    # 计算本月的统计数据
    total_employees = Employee.query.count()
    
    # 获取当月所有员工的健康记录
    health_records = EmployeeHealthRecord.query.filter(
        db.extract('year', EmployeeHealthRecord.record_date) == year,
        db.extract('month', EmployeeHealthRecord.record_date) == month
    ).all()
    
    # 统计适合工作和不适合工作的人数
    available_count = len([r for r in health_records if r.work_suitability])
    unavailable_count = len([r for r in health_records if not r.work_suitability])
    
    # 获取最新的员工健康记录
    latest_records = []
    employees = Employee.query.all()
    
    for employee in employees:
        # 获取该员工最新的健康记录
        latest_record = EmployeeHealthRecord.query.filter_by(
            employee_id=employee.id
        ).order_by(EmployeeHealthRecord.record_date.desc()).first()
        
        if latest_record:
            latest_records.append(latest_record)
    
    # 为每个健康记录添加健康等级和颜色信息
    for record in latest_records:
        record.mental_level, record.mental_color = get_health_level(record.mental_state)
        record.physical_level, record.physical_color = get_health_level(record.physical_health)
    
    # 计算上一个月和下一个月
    prev_date = date(year, month, 1) - timedelta(days=1)
    next_date = date(year, month, calendar.monthrange(year, month)[1]) + timedelta(days=1)
    
    return render_template('health/index.html', 
                         current_year=year,
                         current_month=month,
                         selected_year_month=f"{year}-{month:02d}",
                         total_count=total_employees,
                         available_count=available_count,
                         unavailable_count=unavailable_count,
                         health_records=latest_records,
                         get_health_level=get_health_level,
                         get_health_color=get_health_color)