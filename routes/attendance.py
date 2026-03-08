from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from models import db, Employee, AttendanceRecord, LeaveApplication, OvertimeApplication, Holiday, HolidayDuty
from datetime import datetime, timedelta, date
import pandas as pd
from io import BytesIO
import calendar

# 创建考勤管理蓝图
attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

# 考勤状态映射
attendance_status_map = {
    '1': '正常出勤',
    '换': '换班',
    '值': '值班',
    '年': '年假',
    '病': '病假',
    '事': '事假',
    '产': '产假',
    '婚': '婚假',
    '丧': '丧假',
    '抚': '抚恤假',
    '探': '探亲假',
    '育': '育儿假',
    '伤': '工伤假',
    '旷': '旷工',
    '护': '护理假',
    '休': '休息'
}

# 考勤记录首页
@attendance_bp.route('/')
def index():
    return render_template('attendance/index.html')

# 日考勤管理 - 列表页
@attendance_bp.route('/daily')
def daily_attendance():
    # 获取当前月份，如果有请求参数则使用请求的月份
    current_month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    year, month = map(int, current_month.split('-'))
    
    # 获取当前月份的所有日期
    days_in_month = calendar.monthrange(year, month)[1]
    dates = [date(year, month, day) for day in range(1, days_in_month + 1)]
    
    # 获取所有员工，按排序字段排序
    employees = Employee.query.order_by(Employee.sort_order).all()
    
    # 获取当前月份的所有考勤记录
    attendance_records = AttendanceRecord.query.filter(
        db.extract('year', AttendanceRecord.attendance_date) == year,
        db.extract('month', AttendanceRecord.attendance_date) == month
    ).all()
    
    # 将考勤记录转换为字典，方便查询
    attendance_dict = {(record.employee_id, record.attendance_date): record for record in attendance_records}
    
    return render_template('attendance/daily_attendance.html', 
                          employees=employees, 
                          dates=dates, 
                          current_month=current_month, 
                          attendance_dict=attendance_dict, 
                          attendance_status_map=attendance_status_map)

# 编辑日考勤
@attendance_bp.route('/daily/edit/<int:year>/<int:month>/<int:day>', methods=['GET', 'POST'])
def edit_daily_attendance(year, month, day):
    attendance_date = date(year, month, day)
    
    # 获取所有员工，按排序字段排序
    employees = Employee.query.order_by(Employee.sort_order).all()
    
    if request.method == 'POST':
        # 处理表单提交
        for employee in employees:
            status = request.form.get(f'status_{employee.id}')
            notes = request.form.get(f'notes_{employee.id}', '')
            
            # 查询是否已有考勤记录
            record = AttendanceRecord.query.filter_by(
                employee_id=employee.id,
                attendance_date=attendance_date
            ).first()
            
            if record:
                # 更新现有记录
                record.status = status
                record.notes = notes
                record.updated_by = 'admin'  # 实际应用中应该从登录用户获取
            else:
                # 创建新记录
                new_record = AttendanceRecord(
                    employee_id=employee.id,
                    attendance_date=attendance_date,
                    status=status,
                    notes=notes,
                    created_by='admin',  # 实际应用中应该从登录用户获取
                    updated_by='admin'
                )
                db.session.add(new_record)
        
        db.session.commit()
        flash('考勤记录保存成功！', 'success')
        return redirect(url_for('attendance.daily_attendance', month=f'{year}-{month:02d}'))
    
    # GET请求，获取现有考勤记录
    attendance_records = AttendanceRecord.query.filter_by(attendance_date=attendance_date).all()
    attendance_dict = {record.employee_id: record for record in attendance_records}
    
    return render_template('attendance/edit_daily_attendance.html',
                          employees=employees,
                          attendance_date=attendance_date,
                          attendance_dict=attendance_dict)

# 自动填充节假日和周末
@attendance_bp.route('/auto_fill/<int:year>/<int:month>', methods=['POST'])
def auto_fill_attendance(year, month):
    # 获取当前月份的所有日期
    days_in_month = calendar.monthrange(year, month)[1]
    dates = [date(year, month, day) for day in range(1, days_in_month + 1)]
    
    # 获取所有员工，按排序字段排序
    employees = Employee.query.order_by(Employee.sort_order).all()
    
    # 获取所有节假日
    holidays = Holiday.query.filter(
        db.extract('year', Holiday.holiday_date) == year,
        db.extract('month', Holiday.holiday_date) == month
    ).all()
    holiday_dates = [holiday.holiday_date for holiday in holidays]
    
    for attendance_date in dates:
        # 检查是否是周末或节假日
        is_weekend = attendance_date.weekday() in [5, 6]  # 5=周六, 6=周日
        is_holiday = attendance_date in holiday_dates
        
        if is_weekend or is_holiday:
            for employee in employees:
                # 检查是否已有考勤记录
                record = AttendanceRecord.query.filter_by(
                    employee_id=employee.id,
                    attendance_date=attendance_date
                ).first()
                
                if not record:
                    # 创建休息记录
                    new_record = AttendanceRecord(
                        employee_id=employee.id,
                        attendance_date=attendance_date,
                        status='休',
                        created_by='admin',
                        updated_by='admin'
                    )
                    db.session.add(new_record)
    
    db.session.commit()
    flash('节假日和周末自动填充完成！', 'success')
    return redirect(url_for('attendance.daily_attendance', month=f'{year}-{month:02d}'))

# 请假申请列表
@attendance_bp.route('/leave')
def leave_application_list():
    applications = LeaveApplication.query.order_by(LeaveApplication.created_at.desc()).all()
    return render_template('attendance/leave_application_list.html', applications=applications)

# 提交请假申请
@attendance_bp.route('/leave/add', methods=['GET', 'POST'])
def add_leave_application():
    if request.method == 'POST':
        # 处理表单提交
        employee_id = request.form.get('employee_id')
        leave_type = request.form.get('leave_type')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        duration = float(request.form.get('duration'))
        reason = request.form.get('reason')
        
        # 转换日期时间格式
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        start_time = None
        end_time = None
        if start_time_str:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
        if end_time_str:
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        
        # 处理文件上传
        attachment = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file.filename:
                from werkzeug.utils import secure_filename
                import os
                from app import app
                
                # 检查文件类型
                allowed_extensions = app.config['ALLOWED_EXTENSIONS']
                if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    # 生成安全的文件名
                    filename = secure_filename(file.filename)
                    # 保存文件到上传目录
                    upload_folder = app.config['UPLOAD_FOLDER']
                    # 确保上传目录存在
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    # 保存文件
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    # 保存文件相对路径到数据库
                    attachment = os.path.join('uploads', filename)
        
        # 创建请假申请
        application = LeaveApplication(
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            reason=reason,
            attachment=attachment
        )
        
        db.session.add(application)
        db.session.commit()
        flash('请假申请提交成功！', 'success')
        return redirect(url_for('attendance.leave_application_list'))
    
    # GET请求，渲染表单
    employees = Employee.query.order_by(Employee.sort_order).all()
    return render_template('attendance/leave_application_add.html', employees=employees)

# 审批请假申请
@attendance_bp.route('/leave/approve/<int:application_id>', methods=['GET', 'POST'])
def approve_leave_application(application_id):
    application = LeaveApplication.query.get_or_404(application_id)
    
    if request.method == 'POST':
        action = request.form.get('action')
        comments = request.form.get('comments', '')
        
        # 更新申请状态
        if action == 'approve':
            application.status = 'approved'
            # 自动更新考勤记录
            current_date = application.start_date
            while current_date <= application.end_date:
                record = AttendanceRecord.query.filter_by(
                    employee_id=application.employee_id,
                    attendance_date=current_date
                ).first()
                if record:
                    record.status = application.leave_type
                else:
                    new_record = AttendanceRecord(
                        employee_id=application.employee_id,
                        attendance_date=current_date,
                        status=application.leave_type,
                        created_by='admin',
                        updated_by='admin'
                    )
                    db.session.add(new_record)
                current_date += timedelta(days=1)
        else:
            application.status = 'rejected'
        
        application.approver = 'admin'  # 实际应用中应该从登录用户获取
        application.approval_time = datetime.now()
        application.approval_comments = comments
        
        db.session.commit()
        flash('请假申请审批完成！', 'success')
        return redirect(url_for('attendance.leave_application_list'))
    
    return render_template('attendance/leave_application_approve.html', application=application)

# 加班申请列表
@attendance_bp.route('/overtime')
def overtime_application_list():
    applications = OvertimeApplication.query.order_by(OvertimeApplication.created_at.desc()).all()
    return render_template('attendance/overtime_application_list.html', applications=applications)

# 提交加班申请
@attendance_bp.route('/overtime/add', methods=['GET', 'POST'])
def add_overtime_application():
    if request.method == 'POST':
        # 处理表单提交
        employee_id = request.form.get('employee_id')
        overtime_date_str = request.form.get('overtime_date')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        duration = float(request.form.get('duration'))
        reason = request.form.get('reason')
        
        # 转换日期时间格式
        overtime_date = datetime.strptime(overtime_date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
        
        # 创建加班申请
        application = OvertimeApplication(
            employee_id=employee_id,
            overtime_date=overtime_date,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            reason=reason
        )
        
        db.session.add(application)
        db.session.commit()
        flash('加班申请提交成功！', 'success')
        return redirect(url_for('attendance.overtime_application_list'))
    
    # GET请求，渲染表单
    employees = Employee.query.order_by(Employee.sort_order).all()
    return render_template('attendance/overtime_application_add.html', employees=employees)

# 审批加班申请
@attendance_bp.route('/overtime/approve/<int:application_id>', methods=['GET', 'POST'])
def approve_overtime_application(application_id):
    application = OvertimeApplication.query.get_or_404(application_id)
    
    if request.method == 'POST':
        action = request.form.get('action')
        comments = request.form.get('comments', '')
        
        # 更新申请状态
        application.status = 'approved' if action == 'approve' else 'rejected'
        application.approver = 'admin'  # 实际应用中应该从登录用户获取
        application.approval_time = datetime.now()
        application.approval_comments = comments
        
        db.session.commit()
        flash('加班申请审批完成！', 'success')
        return redirect(url_for('attendance.overtime_application_list'))
    
    return render_template('attendance/overtime_application_approve.html', application=application)

# 节假日管理
@attendance_bp.route('/holidays')
def holiday_list():
    holidays = Holiday.query.order_by(Holiday.holiday_date).all()
    return render_template('attendance/holiday_list.html', holidays=holidays)

# 添加节假日
@attendance_bp.route('/holidays/add', methods=['GET', 'POST'])
def add_holiday():
    if request.method == 'POST':
        holiday_date_str = request.form.get('holiday_date')
        name = request.form.get('name')
        
        # 转换日期格式
        holiday_date = datetime.strptime(holiday_date_str, '%Y-%m-%d').date()
        
        # 检查是否已有该日期的节假日
        existing = Holiday.query.filter_by(holiday_date=holiday_date).first()
        if existing:
            flash('该日期已存在节假日！', 'danger')
            return redirect(url_for('attendance.holiday_list'))
        
        # 创建节假日
        holiday = Holiday(
            holiday_date=holiday_date,
            name=name
        )
        
        db.session.add(holiday)
        db.session.commit()
        flash('节假日添加成功！', 'success')
        return redirect(url_for('attendance.holiday_list'))
    
    return render_template('attendance/holiday_add.html')

# 删除节假日
@attendance_bp.route('/holidays/delete/<int:holiday_id>')
def delete_holiday(holiday_id):
    holiday = Holiday.query.get_or_404(holiday_id)
    db.session.delete(holiday)
    db.session.commit()
    flash('节假日删除成功！', 'success')
    return redirect(url_for('attendance.holiday_list'))


# 节假日值班安排列表
@attendance_bp.route('/holidays/duties/<int:holiday_id>')
def holiday_duty_list(holiday_id):
    holiday = Holiday.query.get_or_404(holiday_id)
    duties = HolidayDuty.query.filter_by(holiday_id=holiday_id).order_by(HolidayDuty.duty_time).all()
    return render_template('attendance/holiday_duty_list.html', holiday=holiday, duties=duties)


# 添加节假日值班安排
@attendance_bp.route('/holidays/duties/add/<int:holiday_id>', methods=['GET', 'POST'])
def add_holiday_duty(holiday_id):
    holiday = Holiday.query.get_or_404(holiday_id)
    employees = Employee.query.order_by(Employee.name).all()
    
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        duty_time = request.form.get('duty_time')
        contact_info = request.form.get('contact_info')
        
        # 检查是否已存在相同员工和时段的值班安排
        existing = HolidayDuty.query.filter_by(
            holiday_id=holiday_id,
            employee_id=employee_id,
            duty_time=duty_time
        ).first()
        
        if existing:
            flash('该员工在该时段已存在值班安排！', 'danger')
            return redirect(url_for('attendance.add_holiday_duty', holiday_id=holiday_id))
        
        # 创建值班安排
        duty = HolidayDuty(
            holiday_id=holiday_id,
            employee_id=employee_id,
            duty_time=duty_time,
            contact_info=contact_info
        )
        
        db.session.add(duty)
        db.session.commit()
        flash('值班安排添加成功！', 'success')
        return redirect(url_for('attendance.holiday_duty_list', holiday_id=holiday_id))
    
    return render_template('attendance/holiday_duty_add.html', holiday=holiday, employees=employees)


# 编辑节假日值班安排
@attendance_bp.route('/holidays/duties/edit/<int:duty_id>', methods=['GET', 'POST'])
def edit_holiday_duty(duty_id):
    duty = HolidayDuty.query.get_or_404(duty_id)
    employees = Employee.query.order_by(Employee.name).all()
    
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        duty_time = request.form.get('duty_time')
        contact_info = request.form.get('contact_info')
        
        # 检查是否已存在相同员工和时段的值班安排（排除当前记录）
        existing = HolidayDuty.query.filter(
            HolidayDuty.holiday_id == duty.holiday_id,
            HolidayDuty.employee_id == employee_id,
            HolidayDuty.duty_time == duty_time,
            HolidayDuty.id != duty_id
        ).first()
        
        if existing:
            flash('该员工在该时段已存在值班安排！', 'danger')
            return redirect(url_for('attendance.edit_holiday_duty', duty_id=duty_id))
        
        # 更新值班安排
        duty.employee_id = employee_id
        duty.duty_time = duty_time
        duty.contact_info = contact_info
        
        db.session.commit()
        flash('值班安排更新成功！', 'success')
        return redirect(url_for('attendance.holiday_duty_list', holiday_id=duty.holiday_id))
    
    return render_template('attendance/holiday_duty_edit.html', duty=duty, employees=employees)


# 删除节假日值班安排
@attendance_bp.route('/holidays/duties/delete/<int:duty_id>')
def delete_holiday_duty(duty_id):
    duty = HolidayDuty.query.get_or_404(duty_id)
    holiday_id = duty.holiday_id
    db.session.delete(duty)
    db.session.commit()
    flash('值班安排删除成功！', 'success')
    return redirect(url_for('attendance.holiday_duty_list', holiday_id=holiday_id))

# 考勤报表
@attendance_bp.route('/report')
def attendance_report():
    employees = Employee.query.all()
    return render_template('attendance/report.html', employees=employees)

# 生成考勤报表
@attendance_bp.route('/report/generate', methods=['POST'])
def generate_attendance_report():
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    employee_id = request.form.get('employee_id')
    
    # 转换日期格式
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    
    # 查询考勤记录
    query = AttendanceRecord.query.filter(
        AttendanceRecord.attendance_date >= start_date,
        AttendanceRecord.attendance_date <= end_date
    )
    
    if employee_id:
        query = query.filter_by(employee_id=int(employee_id))
    
    records = query.all()
    
    # 准备数据
    data = []
    for record in records:
        data.append({
            '员工编号': record.employee.employee_id,
            '员工姓名': record.employee.name,
            '考勤日期': record.attendance_date.strftime('%Y-%m-%d'),
            '考勤状态': attendance_status_map.get(record.status, record.status),
            '上班时间': record.check_in_time.strftime('%H:%M') if record.check_in_time else '',
            '下班时间': record.check_out_time.strftime('%H:%M') if record.check_out_time else '',
            '备注': record.notes or ''
        })
    
    # 创建DataFrame并导出为Excel
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='考勤报表')
    output.seek(0)
    
    return send_file(output, 
                     download_name=f'考勤报表_{start_date_str}_{end_date_str}.xlsx',
                     as_attachment=True)

# 考勤统计
@attendance_bp.route('/statistics')
def attendance_statistics():
    # 获取当前月份，如果有请求参数则使用请求的月份
    current_month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    year, month = map(int, current_month.split('-'))
    
    # 获取所有员工，按排序字段排序
    employees = Employee.query.order_by(Employee.sort_order).all()
    
    # 统计每个员工的考勤情况
    statistics = []
    for employee in employees:
        # 获取当前月份的考勤记录
        records = AttendanceRecord.query.filter(
            AttendanceRecord.employee_id == employee.id,
            db.extract('year', AttendanceRecord.attendance_date) == year,
            db.extract('month', AttendanceRecord.attendance_date) == month
        ).all()
        
        # 计算各种状态的天数
        status_count = {}
        for record in records:
            status_count[record.status] = status_count.get(record.status, 0) + 1
        
        statistics.append({
            'employee': employee,
            'status_count': status_count,
            'total_days': len(records)
        })
    
    return render_template('attendance/statistics.html', 
                          employees=employees, 
                          statistics=statistics, 
                          current_month=current_month, 
                          attendance_status_map=attendance_status_map)

# 考勤异常查询
@attendance_bp.route('/exceptions')
def attendance_exceptions():
    # 查询所有考勤异常记录（迟到、早退、旷工）
    exceptions = AttendanceRecord.query.filter(
        AttendanceRecord.status.in_(['旷', '迟到', '早退'])
    ).order_by(AttendanceRecord.attendance_date.desc()).all()
    
    return render_template('attendance/exceptions.html', exceptions=exceptions, attendance_status_map=attendance_status_map)