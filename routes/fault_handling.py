from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from models import db, Equipment, FaultRecord, FaultSolution
from datetime import datetime
import os
from werkzeug.utils import secure_filename

# 创建蓝图
fault_handling_bp = Blueprint('fault_handling', __name__)

# 故障记录列表页
@fault_handling_bp.route('/records/')
def fault_record_index():
    """故障记录列表页"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    equipment_id = request.args.get('equipment_id', type=int)
    status = request.args.get('status')
    per_page = 10
    
    # 构建查询
    query = FaultRecord.query
    
    if equipment_id:
        query = query.filter_by(equipment_id=equipment_id)
    
    if status:
        query = query.filter_by(status=status)
    
    # 按创建时间倒序排列
    pagination = query.order_by(FaultRecord.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    fault_records = pagination.items
    
    # 获取所有设备
    equipments = Equipment.query.all()
    
    return render_template('fault_handling/record_index.html', 
                          fault_records=fault_records, 
                          pagination=pagination, 
                          selected_equipment=equipment_id, 
                          selected_status=status,
                          equipments=equipments)

# 添加故障记录页面
@fault_handling_bp.route('/records/add/', methods=['GET', 'POST'])
def add_fault_record():
    """添加故障记录页面"""
    # 获取所有设备
    equipments = Equipment.query.all()
    
    if request.method == 'POST':
        # 获取表单数据
        equipment_id = request.form['equipment_id']
        fault_phenomenon = request.form['fault_phenomenon']
        occurrence_date_str = request.form['occurrence_date']
        occurrence_time_str = request.form['occurrence_time']
        reporter = request.form['reporter']
        fault_type = request.form.get('fault_type')
        
        # 新增：故障影响程度和紧急程度
        impact_level = request.form.get('impact_level')
        urgency_level = request.form.get('urgency_level')
        
        # 合并日期和时间
        occurrence_datetime_str = f"{occurrence_date_str} {occurrence_time_str}"
        occurrence_time = datetime.strptime(occurrence_datetime_str, '%Y-%m-%d %H:%M')
        
        # 处理文件上传
        fault_image = None
        if 'fault_image' in request.files and request.files['fault_image'].filename != '':
            file = request.files['fault_image']
            filename = secure_filename(file.filename)
            # 生成唯一的文件名
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            ext = os.path.splitext(filename)[1]
            unique_filename = f"fault_{timestamp}_{filename}"
            
            # 保存文件到上传目录
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            fault_image = unique_filename
        
        # 创建新故障记录
        new_record = FaultRecord(
            equipment_id=equipment_id,
            fault_phenomenon=fault_phenomenon,
            occurrence_time=occurrence_time,
            reporter=reporter,
            fault_type=fault_type,
            fault_image=fault_image,
            impact_level=impact_level,
            urgency_level=urgency_level
        )
        
        # 保存到数据库
        db.session.add(new_record)
        db.session.commit()
        
        flash('故障记录添加成功！', 'success')
        return redirect(url_for('fault_handling.fault_record_index'))
    
    return render_template('fault_handling/record_add.html', equipments=equipments)

# 编辑故障记录页面
@fault_handling_bp.route('/records/edit/<int:id>/', methods=['GET', 'POST'])
def edit_fault_record(id):
    """编辑故障记录页面"""
    # 获取故障记录
    fault_record = FaultRecord.query.get_or_404(id)
    
    # 获取所有设备
    equipments = Equipment.query.all()
    
    if request.method == 'POST':
        # 获取表单数据
        fault_record.equipment_id = request.form['equipment_id']
        fault_record.fault_phenomenon = request.form['fault_phenomenon']
        occurrence_date_str = request.form['occurrence_date']
        occurrence_time_str = request.form['occurrence_time']
        
        # 合并日期和时间
        occurrence_datetime_str = f"{occurrence_date_str} {occurrence_time_str}"
        fault_record.occurrence_time = datetime.strptime(occurrence_datetime_str, '%Y-%m-%d %H:%M')
        
        fault_record.reporter = request.form['reporter']
        fault_record.fault_type = request.form.get('fault_type')
        fault_record.status = request.form['status']
        
        # 新增：故障影响程度和紧急程度
        fault_record.impact_level = request.form.get('impact_level')
        fault_record.urgency_level = request.form.get('urgency_level')
        
        # 处理文件上传
        if 'fault_image' in request.files and request.files['fault_image'].filename != '':
            file = request.files['fault_image']
            filename = secure_filename(file.filename)
            # 生成唯一的文件名
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            ext = os.path.splitext(filename)[1]
            unique_filename = f"fault_{timestamp}_{filename}"
            
            # 保存文件到上传目录
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            # 删除旧图片
            if fault_record.fault_image:
                old_file_path = os.path.join(upload_folder, fault_record.fault_image)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            fault_record.fault_image = unique_filename
        
        # 保存到数据库
        db.session.commit()
        
        flash('故障记录编辑成功！', 'success')
        return redirect(url_for('fault_handling.fault_record_index'))
    
    return render_template('fault_handling/record_edit.html', fault_record=fault_record, equipments=equipments)

# 删除故障记录
@fault_handling_bp.route('/records/delete/<int:id>/', methods=['POST'])
def delete_fault_record(id):
    """删除故障记录"""
    # 获取故障记录
    fault_record = FaultRecord.query.get_or_404(id)
    
    # 删除故障记录
    db.session.delete(fault_record)
    db.session.commit()
    
    flash('故障记录删除成功！', 'success')
    return redirect(url_for('fault_handling.fault_record_index'))

# 故障处理页面（添加解决方案）
@fault_handling_bp.route('/solutions/add/<int:fault_id>/', methods=['GET', 'POST'])
def add_fault_solution(fault_id):
    """添加故障解决方案"""
    # 获取故障记录
    fault_record = FaultRecord.query.get_or_404(fault_id)
    
    if request.method == 'POST':
        # 获取表单数据
        handler = request.form['handler']
        start_date_str = request.form['start_date']
        start_time_str = request.form['start_time']
        end_date_str = request.form.get('end_date')
        end_time_str = request.form.get('end_time')
        process_description = request.form.get('process_description')
        solution = request.form['solution']
        verification_result = request.form.get('verification_result')
        notes = request.form.get('notes')
        
        # 新增：备件使用和维修成本
        spare_parts_used = request.form.get('spare_parts_used')
        repair_cost = request.form.get('repair_cost')
        
        # 合并日期和时间
        start_datetime_str = f"{start_date_str} {start_time_str}"
        start_time = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
        
        end_time = None
        if end_date_str and end_time_str:
            end_datetime_str = f"{end_date_str} {end_time_str}"
            end_time = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M')
        
        # 创建新解决方案
        new_solution = FaultSolution(
            fault_id=fault_id,
            handler=handler,
            start_time=start_time,
            end_time=end_time,
            process_description=process_description,
            solution=solution,
            verification_result=verification_result,
            notes=notes,
            spare_parts_used=spare_parts_used,
            repair_cost=float(repair_cost) if repair_cost else None
        )
        
        # 保存到数据库
        db.session.add(new_solution)
        
        # 更新故障状态为已解决
        if verification_result == 'passed' and end_time:
            fault_record.status = 'resolved'
        elif verification_result == 'failed':
            fault_record.status = 'in_progress'
        else:
            fault_record.status = 'in_progress'
        
        db.session.commit()
        
        flash('故障解决方案添加成功！', 'success')
        return redirect(url_for('fault_handling.view_fault_record', id=fault_id))
    
    return render_template('fault_handling/solution_add.html', fault_record=fault_record)

# 查看故障记录详情
@fault_handling_bp.route('/records/<int:id>/')
def view_fault_record(id):
    """查看故障记录详情"""
    # 获取故障记录
    fault_record = FaultRecord.query.get_or_404(id)
    
    # 获取解决方案列表
    solutions = FaultSolution.query.filter_by(fault_id=id).order_by(FaultSolution.created_at.desc()).all()
    
    return render_template('fault_handling/record_detail.html', fault_record=fault_record, solutions=solutions)

# 故障统计分析页
@fault_handling_bp.route('/statistics/')
def fault_statistics():
    """故障统计分析页"""
    # 故障记录数量统计
    total_faults = FaultRecord.query.count()
    
    # 按状态统计
    status_counts = db.session.query(
        FaultRecord.status,
        db.func.count(FaultRecord.id)
    ).group_by(FaultRecord.status).all()
    
    status_count_dict = {
        'reported': 0,
        'in_progress': 0,
        'resolved': 0,
        'closed': 0
    }
    
    for status, count in status_counts:
        status_count_dict[status] = count
    
    # 按故障类型统计
    type_counts = db.session.query(
        FaultRecord.fault_type,
        db.func.count(FaultRecord.id)
    ).group_by(FaultRecord.fault_type).all()
    
    # 按设备统计故障数量
    equipment_counts = db.session.query(
        Equipment.name,
        db.func.count(FaultRecord.id)
    ).join(FaultRecord).group_by(Equipment.name).all()
    
    # 故障处理时长统计
    resolved_faults = FaultRecord.query.filter_by(status='resolved').all()
    total_duration = 0
    resolved_count = 0
    
    for fault in resolved_faults:
        solutions = FaultSolution.query.filter_by(fault_id=fault.id, verification_result='passed').order_by(FaultSolution.end_time.desc()).all()
        if solutions:
            solution = solutions[0]
            if solution.handling_duration:
                total_duration += solution.handling_duration
                resolved_count += 1
    
    avg_duration = total_duration / resolved_count if resolved_count > 0 else 0
    
    return render_template('fault_handling/statistics.html',
                          total_faults=total_faults,
                          status_count_dict=status_count_dict,
                          type_counts=type_counts,
                          equipment_counts=equipment_counts,
                          avg_duration=avg_duration)

# 故障案例查询页
@fault_handling_bp.route('/cases/')
def fault_cases():
    """故障案例查询页"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword')
    equipment_id = request.args.get('equipment_id', type=int)
    fault_type = request.args.get('fault_type')
    per_page = 10
    
    # 构建查询
    query = FaultRecord.query.filter_by(status='resolved')
    
    if keyword:
        query = query.filter(
            (FaultRecord.fault_phenomenon.like(f'%{keyword}%')) |
            (FaultRecord.fault_type.like(f'%{keyword}%'))
        )
    
    if equipment_id:
        query = query.filter_by(equipment_id=equipment_id)
    
    if fault_type:
        query = query.filter_by(fault_type=fault_type)
    
    # 按创建时间倒序排列
    pagination = query.order_by(FaultRecord.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    cases = pagination.items
    
    # 获取所有设备和故障类型
    equipments = Equipment.query.all()
    fault_types = db.session.query(FaultRecord.fault_type).distinct().filter(FaultRecord.fault_type.isnot(None)).all()
    fault_types = [ft[0] for ft in fault_types if ft[0]]
    
    return render_template('fault_handling/cases.html', 
                          cases=cases, 
                          pagination=pagination, 
                          keyword=keyword,
                          selected_equipment=equipment_id,
                          selected_fault_type=fault_type,
                          equipments=equipments,
                          fault_types=fault_types)

# 关闭故障记录
@fault_handling_bp.route('/records/close/<int:id>/', methods=['POST'])
def close_fault_record(id):
    """关闭故障记录"""
    # 获取故障记录
    fault_record = FaultRecord.query.get_or_404(id)
    
    # 更新状态为已关闭
    fault_record.status = 'closed'
    db.session.commit()
    
    flash('故障记录已关闭！', 'success')
    return redirect(url_for('fault_handling.fault_record_index'))