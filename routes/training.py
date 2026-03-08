from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from models import db, TrainingPlan, TrainingParticipant, TrainingMaterial, TrainingEvaluation, TrainingCertificate, Employee
from datetime import datetime
import os
from werkzeug.utils import secure_filename

# 创建蓝图
training_bp = Blueprint('training', __name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 培训计划列表页
@training_bp.route('/plans/')
def training_plan_index():
    """培训计划列表页"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    keyword = request.args.get('keyword')
    per_page = 10
    
    # 构建查询
    query = TrainingPlan.query
    
    if status:
        query = query.filter_by(status=status)
    
    if keyword:
        query = query.filter(TrainingPlan.title.like(f'%{keyword}%') | TrainingPlan.trainer.like(f'%{keyword}%'))
    
    # 按创建时间倒序排列
    pagination = query.order_by(TrainingPlan.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    training_plans = pagination.items
    
    return render_template('training/plan_index.html', 
                          training_plans=training_plans, 
                          pagination=pagination,
                          selected_status=status,
                          keyword=keyword)

# 添加培训计划页面
@training_bp.route('/plans/add/', methods=['GET', 'POST'])
def add_training_plan():
    """添加培训计划页面"""
    if request.method == 'POST':
        # 获取表单数据
        title = request.form['title']
        description = request.form.get('description')
        trainer = request.form['trainer']
        start_date_str = request.form['start_date']
        start_time_str = request.form['start_time']
        end_date_str = request.form['end_date']
        end_time_str = request.form['end_time']
        location = request.form['location']
        status = request.form['status']
        created_by = request.form['created_by']
        
        # 合并日期和时间
        start_datetime_str = f"{start_date_str} {start_time_str}"
        end_datetime_str = f"{end_date_str} {end_time_str}"
        
        # 转换日期时间
        start_date = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
        end_date = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M')
        
        # 创建新培训计划
        new_plan = TrainingPlan(
            title=title,
            description=description,
            trainer=trainer,
            start_date=start_date,
            end_date=end_date,
            location=location,
            status=status,
            created_by=created_by
        )
        
        # 保存到数据库
        db.session.add(new_plan)
        db.session.commit()
        
        flash('培训计划添加成功！', 'success')
        return redirect(url_for('training.training_plan_index'))
    
    return render_template('training/plan_add.html')

# 编辑培训计划页面
@training_bp.route('/plans/edit/<int:id>/', methods=['GET', 'POST'])
def edit_training_plan(id):
    """编辑培训计划页面"""
    # 获取培训计划
    plan = TrainingPlan.query.get_or_404(id)
    
    if request.method == 'POST':
        # 获取表单数据
        plan.title = request.form['title']
        plan.description = request.form.get('description')
        plan.trainer = request.form['trainer']
        start_date_str = request.form['start_date']
        start_time_str = request.form['start_time']
        end_date_str = request.form['end_date']
        end_time_str = request.form['end_time']
        plan.location = request.form['location']
        plan.status = request.form['status']
        
        # 合并日期和时间
        start_datetime_str = f"{start_date_str} {start_time_str}"
        end_datetime_str = f"{end_date_str} {end_time_str}"
        
        # 转换日期时间
        plan.start_date = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
        plan.end_date = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M')
        
        # 保存到数据库
        db.session.commit()
        
        flash('培训计划编辑成功！', 'success')
        return redirect(url_for('training.training_plan_index'))
    
    return render_template('training/plan_edit.html', plan=plan)

# 删除培训计划
@training_bp.route('/plans/delete/<int:id>/', methods=['POST'])
def delete_training_plan(id):
    """删除培训计划"""
    # 获取培训计划
    plan = TrainingPlan.query.get_or_404(id)
    
    # 删除计划
    db.session.delete(plan)
    db.session.commit()
    
    flash('培训计划删除成功！', 'success')
    return redirect(url_for('training.training_plan_index'))

# 培训计划详情页
@training_bp.route('/plans/<int:id>/')
def training_plan_detail(id):
    """培训计划详情页"""
    # 获取培训计划
    plan = TrainingPlan.query.get_or_404(id)
    
    # 获取参与人员列表
    participants = TrainingParticipant.query.filter_by(training_id=id).all()
    
    # 获取培训资料列表
    materials = TrainingMaterial.query.filter_by(training_id=id).all()
    
    # 获取培训评估列表
    evaluations = TrainingEvaluation.query.filter_by(training_id=id).all()
    
    # 获取培训证书列表
    certificates = TrainingCertificate.query.filter_by(training_id=id).all()
    
    return render_template('training/plan_detail.html', 
                          plan=plan, 
                          participants=participants,
                          materials=materials,
                          evaluations=evaluations,
                          certificates=certificates)

# 参与人员管理页面
@training_bp.route('/plans/<int:plan_id>/participants/', methods=['GET', 'POST'])
def manage_participants(plan_id):
    """参与人员管理页面"""
    # 获取培训计划
    plan = TrainingPlan.query.get_or_404(plan_id)
    
    # 获取所有员工
    all_employees = Employee.query.all()
    
    # 获取已添加的参与人员
    participants = TrainingParticipant.query.filter_by(training_id=plan_id).all()
    participant_employee_ids = [p.employee_id for p in participants]
    
    if request.method == 'POST':
        # 获取表单数据
        employee_ids = request.form.getlist('employee_ids')
        
        # 删除已有的参与人员
        TrainingParticipant.query.filter_by(training_id=plan_id).delete()
        
        # 添加新的参与人员
        for employee_id in employee_ids:
            participant = TrainingParticipant(
                training_id=plan_id,
                employee_id=employee_id
            )
            db.session.add(participant)
        
        db.session.commit()
        flash('参与人员更新成功！', 'success')
        return redirect(url_for('training.training_plan_detail', id=plan_id))
    
    return render_template('training/manage_participants.html', 
                          plan=plan, 
                          all_employees=all_employees,
                          participant_employee_ids=participant_employee_ids)

# 更新参与人员考核结果
@training_bp.route('/participants/<int:id>/update/', methods=['POST'])
def update_participant(id):
    """更新参与人员考核结果"""
    # 获取参与人员
    participant = TrainingParticipant.query.get_or_404(id)
    
    # 获取表单数据
    participant.attendance = request.form.get('attendance') == 'true'
    score = request.form.get('score')
    participant.score = float(score) if score else None
    participant.assessment = request.form.get('assessment')
    
    # 保存到数据库
    db.session.commit()
    
    flash('考核结果更新成功！', 'success')
    return redirect(url_for('training.training_plan_detail', id=participant.training_id))

# 上传培训资料页面
@training_bp.route('/plans/<int:plan_id>/materials/add/', methods=['GET', 'POST'])
def add_training_material(plan_id):
    """上传培训资料页面"""
    # 获取培训计划
    plan = TrainingPlan.query.get_or_404(plan_id)
    
    if request.method == 'POST':
        # 获取表单数据
        title = request.form['title']
        description = request.form.get('description')
        uploaded_by = request.form['uploaded_by']
        
        # 处理文件上传
        if 'file' not in request.files:
            flash('请选择要上传的文件！', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('请选择要上传的文件！', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # 确保uploads目录存在
            upload_folder = os.path.join(os.getcwd(), 'static', 'uploads', 'training_materials')
            os.makedirs(upload_folder, exist_ok=True)
            
            # 保存文件
            filename = secure_filename(f"{plan_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # 获取文件类型
            file_type = filename.rsplit('.', 1)[1].lower()
            
            # 创建培训资料记录
            new_material = TrainingMaterial(
                training_id=plan_id,
                title=title,
                file_path=f"uploads/training_materials/{filename}",
                file_type=file_type,
                description=description,
                uploaded_by=uploaded_by
            )
            
            # 保存到数据库
            db.session.add(new_material)
            db.session.commit()
            
            flash('培训资料上传成功！', 'success')
            return redirect(url_for('training.training_plan_detail', id=plan_id))
        else:
            flash('不支持的文件类型！', 'danger')
            return redirect(request.url)
    
    return render_template('training/material_add.html', plan=plan)

# 下载培训资料
@training_bp.route('/materials/<int:id>/download/')
def download_training_material(id):
    """下载培训资料"""
    # 获取培训资料
    material = TrainingMaterial.query.get_or_404(id)
    
    # 构建完整的文件路径
    file_path = os.path.join(os.getcwd(), 'static', material.file_path)
    
    # 返回文件
    return send_file(file_path, as_attachment=True, download_name=material.title)

# 删除培训资料
@training_bp.route('/materials/<int:id>/delete/', methods=['POST'])
def delete_training_material(id):
    """删除培训资料"""
    # 获取培训资料
    material = TrainingMaterial.query.get_or_404(id)
    plan_id = material.training_id
    
    # 删除文件
    file_path = os.path.join(os.getcwd(), 'static', material.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 删除记录
    db.session.delete(material)
    db.session.commit()
    
    flash('培训资料删除成功！', 'success')
    return redirect(url_for('training.training_plan_detail', id=plan_id))

# 添加培训评估页面
@training_bp.route('/plans/<int:plan_id>/evaluations/add/', methods=['GET', 'POST'])
def add_training_evaluation(plan_id):
    """添加培训评估页面"""
    # 获取培训计划
    plan = TrainingPlan.query.get_or_404(plan_id)
    
    if request.method == 'POST':
        # 获取表单数据
        evaluator = request.form['evaluator']
        content_relevance = int(request.form['content_relevance'])
        trainer_effectiveness = int(request.form['trainer_effectiveness'])
        overall_satisfaction = int(request.form['overall_satisfaction'])
        comments = request.form.get('comments')
        
        # 创建培训评估
        evaluation = TrainingEvaluation(
            training_id=plan_id,
            evaluator=evaluator,
            content_relevance=content_relevance,
            trainer_effectiveness=trainer_effectiveness,
            overall_satisfaction=overall_satisfaction,
            comments=comments
        )
        
        # 保存到数据库
        db.session.add(evaluation)
        db.session.commit()
        
        flash('培训评估添加成功！', 'success')
        return redirect(url_for('training.training_plan_detail', id=plan_id))
    
    return render_template('training/evaluation_add.html', plan=plan)

# 添加培训证书页面
@training_bp.route('/plans/<int:plan_id>/certificates/add/', methods=['GET', 'POST'])
def add_training_certificate(plan_id):
    """添加培训证书页面"""
    # 获取培训计划
    plan = TrainingPlan.query.get_or_404(plan_id)
    
    # 获取参与人员
    participants = TrainingParticipant.query.filter_by(training_id=plan_id, attendance=True).all()
    
    if request.method == 'POST':
        # 获取表单数据
        employee_id = request.form['employee_id']
        certificate_number = request.form['certificate_number']
        issue_date_str = request.form['issue_date']
        valid_until_str = request.form.get('valid_until')
        
        # 转换日期
        issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
        valid_until = datetime.strptime(valid_until_str, '%Y-%m-%d').date() if valid_until_str else None
        
        # 创建培训证书
        certificate = TrainingCertificate(
            training_id=plan_id,
            employee_id=employee_id,
            certificate_number=certificate_number,
            issue_date=issue_date,
            valid_until=valid_until
        )
        
        # 保存到数据库
        db.session.add(certificate)
        db.session.commit()
        
        flash('培训证书添加成功！', 'success')
        return redirect(url_for('training.training_plan_detail', id=plan_id))
    
    return render_template('training/certificate_add.html', plan=plan, participants=participants)

# 培训统计分析页
@training_bp.route('/statistics/')
def training_statistics():
    """培训统计分析页"""
    # 总培训计划数
    total_plans = TrainingPlan.query.count()
    
    # 按状态统计
    status_counts = db.session.query(
        TrainingPlan.status,
        db.func.count(TrainingPlan.id)
    ).group_by(TrainingPlan.status).all()
    
    status_count_dict = {
        'planned': 0,
        'in_progress': 0,
        'completed': 0,
        'cancelled': 0
    }
    
    for status, count in status_counts:
        status_count_dict[status] = count
    
    # 参与人数统计
    total_participants = TrainingParticipant.query.count()
    attendance_rate = 0
    
    if total_participants > 0:
        attended_count = TrainingParticipant.query.filter_by(attendance=True).count()
        attendance_rate = (attended_count / total_participants) * 100
    
    # 培训评估统计
    evaluations = TrainingEvaluation.query.all()
    avg_content_relevance = 0
    avg_trainer_effectiveness = 0
    avg_overall_satisfaction = 0
    
    if evaluations:
        avg_content_relevance = sum(e.content_relevance for e in evaluations) / len(evaluations)
        avg_trainer_effectiveness = sum(e.trainer_effectiveness for e in evaluations) / len(evaluations)
        avg_overall_satisfaction = sum(e.overall_satisfaction for e in evaluations) / len(evaluations)
    
    # 证书统计
    total_certificates = TrainingCertificate.query.count()
    
    return render_template('training/statistics.html',
                          total_plans=total_plans,
                          status_count_dict=status_count_dict,
                          total_participants=total_participants,
                          attendance_rate=attendance_rate,
                          avg_content_relevance=avg_content_relevance,
                          avg_trainer_effectiveness=avg_trainer_effectiveness,
                          avg_overall_satisfaction=avg_overall_satisfaction,
                          total_certificates=total_certificates)

# 证书管理页面
@training_bp.route('/certificates/')
def certificate_management():
    """证书管理页面"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    employee_id = request.args.get('employee_id', type=int)
    per_page = 10
    
    # 构建查询
    query = TrainingCertificate.query
    
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    
    # 按颁发日期倒序排列
    pagination = query.order_by(TrainingCertificate.issue_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    certificates = pagination.items
    
    # 获取所有员工
    employees = Employee.query.all()
    
    return render_template('training/certificate_management.html', 
                          certificates=certificates,
                          pagination=pagination,
                          selected_employee=employee_id,
                          employees=employees)