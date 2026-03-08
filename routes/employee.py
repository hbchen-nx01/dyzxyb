from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from models import db, Employee, SkillLevel, TrainingExperience, QualificationCertificate
from datetime import datetime
import os
import uuid
import pandas as pd
from io import BytesIO

# 创建蓝图
employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/')
def employee_index():
    """员工信息首页，支持查询"""
    # 获取查询参数
    employee_id = request.args.get('employee_id', '')
    name = request.args.get('name', '')
    position = request.args.get('position', '')
    
    # 构建查询
    query = Employee.query
    
    # 按员工编号查询
    if employee_id:
        query = query.filter(Employee.employee_id.like(f'%{employee_id}%'))
    
    # 按姓名查询
    if name:
        query = query.filter(Employee.name.like(f'%{name}%'))
    
    # 按岗位分类查询
    if position:
        query = query.filter(Employee.position.like(f'%{position}%'))
    
    # 按排序字段排序
    employees = query.order_by(Employee.sort_order).all()
    
    return render_template('employee/index.html', employees=employees)

@employee_bp.route('/update-order', methods=['POST'])
def update_employee_order():
    """更新员工顺序"""
    try:
        # 获取排序数据
        order_data = request.get_json()
        
        # 更新每个员工的排序值
        for item in order_data:
            employee = Employee.query.get(item['id'])
            if employee:
                employee.sort_order = item['sort_order']
        
        # 保存到数据库
        db.session.commit()
        
        return jsonify({'success': True, 'message': '员工顺序更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@employee_bp.route('/add', methods=['GET', 'POST'])
def add_employee():
    """添加员工信息"""
    if request.method == 'POST':
        # 获取表单数据
        employee_id = request.form['employee_id']
        name = request.form['name']
        gender = request.form['gender']
        birthday = datetime.strptime(request.form['birthday'], '%Y-%m-%d').date()
        position = request.form['position']
        contact = request.form['contact']
        education = request.form['education']
        school = request.form['school']
        
        # 创建新员工
        new_employee = Employee(
            employee_id=employee_id,
            name=name,
            gender=gender,
            birthday=birthday,
            position=position,
            contact=contact,
            education=education,
            school=school
        )
        
        # 保存到数据库
        db.session.add(new_employee)
        db.session.commit()
        
        flash('员工信息添加成功！', 'success')
        return redirect(url_for('employee.employee_index'))
    
    return render_template('employee/add.html')

@employee_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    """编辑员工信息"""
    employee = Employee.query.get_or_404(id)
    
    if request.method == 'POST':
        # 获取表单数据
        employee.employee_id = request.form['employee_id']
        employee.name = request.form['name']
        employee.gender = request.form['gender']
        employee.birthday = datetime.strptime(request.form['birthday'], '%Y-%m-%d').date()
        employee.position = request.form['position']
        employee.contact = request.form['contact']
        employee.education = request.form['education']
        employee.school = request.form['school']
        
        # 保存到数据库
        db.session.commit()
        
        flash('员工信息编辑成功！', 'success')
        return redirect(url_for('employee.employee_index'))
    
    return render_template('employee/edit.html', employee=employee)

@employee_bp.route('/delete/<int:id>', methods=['POST'])
def delete_employee(id):
    """删除员工信息"""
    employee = Employee.query.get_or_404(id)
    
    # 删除员工信息（级联删除相关的技能等级、培训经历和资质证书）
    db.session.delete(employee)
    db.session.commit()
    
    flash('员工信息删除成功！', 'success')
    return redirect(url_for('employee.employee_index'))

@employee_bp.route('/detail/<int:id>')
def employee_detail(id):
    """员工详情页面，包括技能等级、培训经历和资质证书"""
    employee = Employee.query.get_or_404(id)
    return render_template('employee/detail.html', employee=employee)

# 技能等级管理
@employee_bp.route('/<int:employee_id>/skill-level/add', methods=['GET', 'POST'])
def add_skill_level(employee_id):
    """添加技能等级"""
    employee = Employee.query.get_or_404(employee_id)
    
    if request.method == 'POST':
        # 获取表单数据
        skill_name = request.form['skill_name']
        level = request.form['level']
        obtained_date = datetime.strptime(request.form['obtained_date'], '%Y-%m-%d').date()
        
        # 创建新技能等级
        new_skill_level = SkillLevel(
            employee_id=employee_id,
            skill_name=skill_name,
            level=level,
            obtained_date=obtained_date
        )
        
        # 保存到数据库
        db.session.add(new_skill_level)
        db.session.commit()
        
        flash('技能等级添加成功！', 'success')
        return redirect(url_for('employee.employee_detail', id=employee_id))
    
    return render_template('employee/skill_level/add.html', employee=employee)

@employee_bp.route('/skill-level/edit/<int:id>', methods=['GET', 'POST'])
def edit_skill_level(id):
    """编辑技能等级"""
    skill_level = SkillLevel.query.get_or_404(id)
    
    if request.method == 'POST':
        # 获取表单数据
        skill_level.skill_name = request.form['skill_name']
        skill_level.level = request.form['level']
        skill_level.obtained_date = datetime.strptime(request.form['obtained_date'], '%Y-%m-%d').date()
        
        # 保存到数据库
        db.session.commit()
        
        flash('技能等级编辑成功！', 'success')
        return redirect(url_for('employee.employee_detail', id=skill_level.employee_id))
    
    return render_template('employee/skill_level/edit.html', skill_level=skill_level)

@employee_bp.route('/skill-level/delete/<int:id>', methods=['POST'])
def delete_skill_level(id):
    """删除技能等级"""
    skill_level = SkillLevel.query.get_or_404(id)
    employee_id = skill_level.employee_id
    
    # 删除技能等级
    db.session.delete(skill_level)
    db.session.commit()
    
    flash('技能等级删除成功！', 'success')
    return redirect(url_for('employee.employee_detail', id=employee_id))

# 培训经历管理
@employee_bp.route('/<int:employee_id>/training-experience/add', methods=['GET', 'POST'])
def add_training_experience(employee_id):
    """添加培训经历"""
    employee = Employee.query.get_or_404(employee_id)
    
    if request.method == 'POST':
        # 获取表单数据
        training_name = request.form['training_name']
        training_organization = request.form['training_organization']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        training_content = request.form['training_content']
        
        # 创建新培训经历
        new_training_experience = TrainingExperience(
            employee_id=employee_id,
            training_name=training_name,
            training_organization=training_organization,
            start_date=start_date,
            end_date=end_date,
            training_content=training_content
        )
        
        # 保存到数据库
        db.session.add(new_training_experience)
        db.session.commit()
        
        flash('培训经历添加成功！', 'success')
        return redirect(url_for('employee.employee_detail', id=employee_id))
    
    return render_template('employee/training_experience/add.html', employee=employee)

@employee_bp.route('/training-experience/edit/<int:id>', methods=['GET', 'POST'])
def edit_training_experience(id):
    """编辑培训经历"""
    training_experience = TrainingExperience.query.get_or_404(id)
    
    if request.method == 'POST':
        # 获取表单数据
        training_experience.training_name = request.form['training_name']
        training_experience.training_organization = request.form['training_organization']
        training_experience.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        training_experience.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        training_experience.training_content = request.form['training_content']
        
        # 保存到数据库
        db.session.commit()
        
        flash('培训经历编辑成功！', 'success')
        return redirect(url_for('employee.employee_detail', id=training_experience.employee_id))
    
    return render_template('employee/training_experience/edit.html', training_experience=training_experience)

@employee_bp.route('/training-experience/delete/<int:id>', methods=['POST'])
def delete_training_experience(id):
    """删除培训经历"""
    training_experience = TrainingExperience.query.get_or_404(id)
    employee_id = training_experience.employee_id
    
    # 删除培训经历
    db.session.delete(training_experience)
    db.session.commit()
    
    flash('培训经历删除成功！', 'success')
    return redirect(url_for('employee.employee_detail', id=employee_id))

# 资质证书管理
@employee_bp.route('/<int:employee_id>/qualification-certificate/add', methods=['GET', 'POST'])
def add_qualification_certificate(employee_id):
    """添加资质证书"""
    employee = Employee.query.get_or_404(employee_id)
    
    if request.method == 'POST':
        # 获取表单数据
        certificate_name = request.form['certificate_name']
        certificate_number = request.form['certificate_number']
        issued_by = request.form['issued_by']
        issued_date = datetime.strptime(request.form['issued_date'], '%Y-%m-%d').date()
        valid_until = request.form['valid_until']
        
        # 处理文件上传
        file_path = None
        if 'certificate_file' in request.files:
            file = request.files['certificate_file']
            if file.filename != '':
                # 生成唯一文件名
                file_ext = os.path.splitext(file.filename)[1]
                unique_filename = f'{uuid.uuid4()}{file_ext}'
                
                # 保存文件到上传目录
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(upload_path)
                
                # 保存相对路径到数据库
                file_path = os.path.join('uploads', unique_filename)
        
        # 创建新资质证书
        new_qualification_certificate = QualificationCertificate(
            employee_id=employee_id,
            certificate_name=certificate_name,
            certificate_number=certificate_number,
            issued_by=issued_by,
            issued_date=issued_date,
            valid_until=datetime.strptime(valid_until, '%Y-%m-%d').date() if valid_until else None,
            file_path=file_path
        )
        
        # 保存到数据库
        db.session.add(new_qualification_certificate)
        db.session.commit()
        
        flash('资质证书添加成功！', 'success')
        return redirect(url_for('employee.employee_detail', id=employee_id))
    
    return render_template('employee/qualification_certificate/add.html', employee=employee)

@employee_bp.route('/qualification-certificate/edit/<int:id>', methods=['GET', 'POST'])
def edit_qualification_certificate(id):
    """编辑资质证书"""
    qualification_certificate = QualificationCertificate.query.get_or_404(id)
    
    if request.method == 'POST':
        # 获取表单数据
        qualification_certificate.certificate_name = request.form['certificate_name']
        qualification_certificate.certificate_number = request.form['certificate_number']
        qualification_certificate.issued_by = request.form['issued_by']
        qualification_certificate.issued_date = datetime.strptime(request.form['issued_date'], '%Y-%m-%d').date()
        valid_until = request.form['valid_until']
        qualification_certificate.valid_until = datetime.strptime(valid_until, '%Y-%m-%d').date() if valid_until else None
        
        # 处理文件上传
        if 'certificate_file' in request.files:
            file = request.files['certificate_file']
            if file.filename != '':
                # 如果有旧文件，先删除
                if qualification_certificate.file_path:
                    old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(qualification_certificate.file_path))
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                # 生成唯一文件名
                file_ext = os.path.splitext(file.filename)[1]
                unique_filename = f'{uuid.uuid4()}{file_ext}'
                
                # 保存文件到上传目录
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(upload_path)
                
                # 更新数据库中的文件路径
                qualification_certificate.file_path = os.path.join('uploads', unique_filename)
        
        # 保存到数据库
        db.session.commit()
        
        flash('资质证书编辑成功！', 'success')
        return redirect(url_for('employee.employee_detail', id=qualification_certificate.employee_id))
    
    return render_template('employee/qualification_certificate/edit.html', qualification_certificate=qualification_certificate)

@employee_bp.route('/qualification-certificate/delete/<int:id>', methods=['POST'])
def delete_qualification_certificate(id):
    """删除资质证书"""
    qualification_certificate = QualificationCertificate.query.get_or_404(id)
    employee_id = qualification_certificate.employee_id
    
    # 删除资质证书
    db.session.delete(qualification_certificate)
    db.session.commit()
    
    flash('资质证书删除成功！', 'success')
    return redirect(url_for('employee.employee_detail', id=employee_id))

# Excel导入导出功能
@employee_bp.route('/export-excel')
def export_excel():
    """导出员工信息到Excel"""
    # 查询所有员工
    employees = Employee.query.all()
    
    # 准备数据
    data = []
    for emp in employees:
        data.append({
            '员工编号': emp.employee_id,
            '姓名': emp.name,
            '性别': emp.gender,
            '出生年月日': emp.birthday.strftime('%Y-%m-%d'),
            '岗位分类': emp.position,
            '联系方式': emp.contact,
            '学历': emp.education,
            '院校': emp.school,
            '创建时间': emp.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            '更新时间': emp.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 保存到BytesIO对象
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='员工信息')
    
    # 重置文件指针
    output.seek(0)
    
    # 返回文件
    return send_file(output, as_attachment=True, download_name=f'员工信息_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@employee_bp.route('/import-excel', methods=['GET', 'POST'])
def import_excel():
    """从Excel导入员工信息"""
    if request.method == 'POST':
        # 检查是否有文件上传
        if 'file' not in request.files:
            flash('请选择要上传的Excel文件', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        # 检查文件是否为空
        if file.filename == '':
            flash('请选择要上传的Excel文件', 'danger')
            return redirect(request.url)
        
        # 检查文件类型
        if not file.filename.endswith('.xlsx') and not file.filename.endswith('.xls'):
            flash('请上传Excel文件（.xlsx或.xls）', 'danger')
            return redirect(request.url)
        
        try:
            # 读取Excel文件
            df = pd.read_excel(file)
            
            # 检查必要的列是否存在
            required_columns = ['员工编号', '姓名', '性别', '出生年月日', '岗位分类', '联系方式', '学历', '院校']
            if not all(col in df.columns for col in required_columns):
                flash('Excel文件缺少必要的列，请检查文件格式', 'danger')
                return redirect(request.url)
            
            # 导入数据
            success_count = 0
            for index, row in df.iterrows():
                # 检查员工编号是否已存在
                existing_employee = Employee.query.filter_by(employee_id=str(row['员工编号'])).first()
                if existing_employee:
                    continue
                
                # 创建新员工
                new_employee = Employee(
                    employee_id=str(row['员工编号']),
                    name=str(row['姓名']),
                    gender=str(row['性别']),
                    birthday=pd.to_datetime(row['出生年月日']).date(),
                    position=str(row['岗位分类']),
                    contact=str(row['联系方式']),
                    education=str(row['学历']),
                    school=str(row['院校'])
                )
                
                # 保存到数据库
                db.session.add(new_employee)
                success_count += 1
            
            # 提交事务
            db.session.commit()
            
            flash(f'成功导入 {success_count} 条员工信息', 'success')
            return redirect(url_for('employee.employee_index'))
        except Exception as e:
            flash(f'导入失败：{str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('employee/import_excel.html')
