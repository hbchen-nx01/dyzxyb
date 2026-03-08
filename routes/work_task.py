from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, WorkTask, WorkReport, Employee
from datetime import datetime

# 创建蓝图
work_task_bp = Blueprint('work_task', __name__)

# 工作任务列表页
@work_task_bp.route('/')
def work_task_index():
    """工作任务列表页"""
    # 获取查询参数
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 构建查询
    if status:
        query = WorkTask.query.filter_by(status=status)
    else:
        query = WorkTask.query
    
    # 按创建时间倒序排列
    pagination = query.order_by(WorkTask.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    tasks = pagination.items
    
    # 统计各状态任务数量
    status_counts = {
        'pending': WorkTask.query.filter_by(status='pending').count(),
        'in_progress': WorkTask.query.filter_by(status='in_progress').count(),
        'completed': WorkTask.query.filter_by(status='completed').count()
    }
    
    return render_template('work_task/index.html', tasks=tasks, pagination=pagination, selected_status=status, status_counts=status_counts)

# 添加工作任务页面
@work_task_bp.route('/add/', methods=['GET', 'POST'])
def add_work_task():
    """添加工作任务页面"""
    # 获取所有员工
    employees = Employee.query.all()
    
    if request.method == 'POST':
        # 获取表单数据
        title = request.form['title']
        description = request.form.get('description')
        assigned_type = request.form['assigned_type']
        assigned_to = request.form['assigned_to'] if assigned_type == 'contractor' else request.form['employee_id']
        status = request.form.get('status', 'pending')
        
        # 创建新工作任务
        new_task = WorkTask(
            title=title,
            description=description,
            assigned_to=assigned_to,
            assigned_type=assigned_type,
            status=status
        )
        
        # 如果任务状态是已完成，设置完成时间
        if status == 'completed':
            new_task.completed_at = datetime.utcnow()
        
        # 保存到数据库
        db.session.add(new_task)
        db.session.commit()
        
        flash('工作任务添加成功！', 'success')
        return redirect(url_for('work_task.work_task_index'))
    
    return render_template('work_task/add.html', employees=employees)

# 编辑工作任务页面
@work_task_bp.route('/edit/<int:id>/', methods=['GET', 'POST'])
def edit_work_task(id):
    """编辑工作任务页面"""
    # 获取工作任务
    task = WorkTask.query.get_or_404(id)
    
    # 获取所有员工
    employees = Employee.query.all()
    
    if request.method == 'POST':
        # 获取表单数据
        task.title = request.form['title']
        task.description = request.form.get('description')
        assigned_type = request.form['assigned_type']
        task.assigned_type = assigned_type
        task.assigned_to = request.form['assigned_to'] if assigned_type == 'contractor' else request.form['employee_id']
        
        # 如果状态发生变化
        old_status = task.status
        new_status = request.form['status']
        task.status = new_status
        
        # 如果状态从非完成变为完成，设置完成时间
        if old_status != 'completed' and new_status == 'completed':
            task.completed_at = datetime.utcnow()
        # 如果状态从完成变为非完成，清除完成时间
        elif old_status == 'completed' and new_status != 'completed':
            task.completed_at = None
        
        # 保存到数据库
        db.session.commit()
        
        flash('工作任务编辑成功！', 'success')
        return redirect(url_for('work_task.work_task_index'))
    
    return render_template('work_task/edit.html', task=task, employees=employees)

# 删除工作任务
@work_task_bp.route('/delete/<int:id>/', methods=['POST'])
def delete_work_task(id):
    """删除工作任务"""
    # 获取工作任务
    task = WorkTask.query.get_or_404(id)
    
    # 删除工作任务
    db.session.delete(task)
    db.session.commit()
    
    flash('工作任务删除成功！', 'success')
    return redirect(url_for('work_task.work_task_index'))

# 更新任务状态
@work_task_bp.route('/status/<int:id>/', methods=['POST'])
def update_task_status(id):
    """更新任务状态"""
    # 获取工作任务
    task = WorkTask.query.get_or_404(id)
    
    # 获取新状态
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'in_progress', 'completed']:
        old_status = task.status
        task.status = new_status
        
        # 如果状态从非完成变为完成，设置完成时间
        if old_status != 'completed' and new_status == 'completed':
            task.completed_at = datetime.utcnow()
        # 如果状态从完成变为非完成，清除完成时间
        elif old_status == 'completed' and new_status != 'completed':
            task.completed_at = None
        
        # 保存到数据库
        db.session.commit()
        
        flash('任务状态更新成功！', 'success')
    
    return redirect(url_for('work_task.work_task_index'))

# 工作任务详情页
@work_task_bp.route('/detail/<int:id>/')
def work_task_detail(id):
    """工作任务详情页"""
    # 获取工作任务
    task = WorkTask.query.get_or_404(id)
    
    # 获取相关的工作日报
    reports = sorted(task.reports, key=lambda x: x.report_date, reverse=True)
    
    return render_template('work_task/detail.html', task=task, reports=reports)

# 工作日报列表页
@work_task_bp.route('/report/')
def work_report_index():
    """工作日报列表页"""
    # 获取查询参数
    task_id = request.args.get('task_id', type=int)
    report_date = request.args.get('report_date')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 构建查询
    query = WorkReport.query
    
    if task_id:
        query = query.filter_by(task_id=task_id)
    
    if report_date:
        report_date_obj = datetime.strptime(report_date, '%Y-%m-%d').date()
        query = query.filter_by(report_date=report_date_obj)
    
    # 按报告日期倒序排列
    pagination = query.order_by(WorkReport.report_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    reports = pagination.items
    
    # 获取所有任务
    tasks = WorkTask.query.all()
    
    return render_template('work_task/report_index.html', reports=reports, pagination=pagination, selected_task=task_id, selected_date=report_date, tasks=tasks)

# 添加工作日报页面
@work_task_bp.route('/report/add/<int:task_id>/', methods=['GET', 'POST'])
def add_work_report(task_id):
    """添加工作日报页面"""
    # 获取工作任务
    task = WorkTask.query.get_or_404(task_id)
    
    if request.method == 'POST':
        # 获取表单数据
        report_date_str = request.form.get('report_date')
        content = request.form['content']
        author = request.form['author']
        
        # 处理报告日期
        if report_date_str:
            report_date = datetime.strptime(report_date_str, '%Y-%m-%d').date()
        else:
            report_date = datetime.utcnow().date()
        
        # 创建新工作日报
        new_report = WorkReport(
            task_id=task_id,
            report_date=report_date,
            content=content,
            author=author
        )
        
        # 保存到数据库
        db.session.add(new_report)
        db.session.commit()
        
        flash('工作日报添加成功！', 'success')
        return redirect(url_for('work_task.work_task_detail', id=task_id))
    
    return render_template('work_task/report_add.html', task=task)

# 编辑工作日报页面
@work_task_bp.route('/report/edit/<int:id>/', methods=['GET', 'POST'])
def edit_work_report(id):
    """编辑工作日报页面"""
    # 获取工作日报
    report = WorkReport.query.get_or_404(id)
    
    if request.method == 'POST':
        # 获取表单数据
        report_date_str = request.form.get('report_date')
        content = request.form['content']
        author = request.form['author']
        
        # 处理报告日期
        if report_date_str:
            report.report_date = datetime.strptime(report_date_str, '%Y-%m-%d').date()
        
        report.content = content
        report.author = author
        
        # 保存到数据库
        db.session.commit()
        
        flash('工作日报编辑成功！', 'success')
        return redirect(url_for('work_task.work_task_detail', id=report.task_id))
    
    return render_template('work_task/report_edit.html', report=report)

# 删除工作日报
@work_task_bp.route('/report/delete/<int:id>/', methods=['POST'])
def delete_work_report(id):
    """删除工作日报"""
    # 获取工作日报
    report = WorkReport.query.get_or_404(id)
    task_id = report.task_id
    
    # 删除工作日报
    db.session.delete(report)
    db.session.commit()
    
    flash('工作日报删除成功！', 'success')
    return redirect(url_for('work_task.work_task_detail', id=task_id))

# 工作统计分析页
@work_task_bp.route('/statistics/')
def work_statistics():
    """工作统计分析页"""
    # 任务状态统计
    status_counts = {
        'pending': WorkTask.query.filter_by(status='pending').count(),
        'in_progress': WorkTask.query.filter_by(status='in_progress').count(),
        'completed': WorkTask.query.filter_by(status='completed').count()
    }
    
    # 人员工作量统计（按任务数量）
    tasks = WorkTask.query.all()
    personnel_workload = {}
    for task in tasks:
        if task.assigned_to in personnel_workload:
            personnel_workload[task.assigned_to] += 1
        else:
            personnel_workload[task.assigned_to] = 1
    
    # 任务完成趋势（按周统计）
    # 这里简化处理，按日期统计最近30天的完成任务数
    import datetime as dt
    today = datetime.utcnow().date()
    start_date = today - dt.timedelta(days=29)  # 最近30天
    
    # 生成日期列表
    date_list = [start_date + dt.timedelta(days=i) for i in range(30)]
    completed_tasks_by_date = {}
    
    for date in date_list:
        # 对于SQLite，使用字符串比较来匹配日期
        date_str = date.strftime('%Y-%m-%d')
        completed_tasks_by_date[date_str] = WorkTask.query.filter(
            WorkTask.status == 'completed',
            WorkTask.completed_at.isnot(None),
            db.func.strftime('%Y-%m-%d', WorkTask.completed_at) == date_str
        ).count()
    
    return render_template('work_task/statistics.html', 
                          status_counts=status_counts,
                          personnel_workload=personnel_workload,
                          completed_tasks_by_date=completed_tasks_by_date)
