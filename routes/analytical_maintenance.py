from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Equipment, MaintenancePlan, MaintenanceRecord, FaultRecord, FaultSolution
from datetime import datetime

# 创建蓝图
analytical_maintenance_bp = Blueprint('analytical_maintenance', __name__)

# 仪表维护仪表盘
@analytical_maintenance_bp.route('/')
def dashboard():
    """仪表维护仪表盘"""
    # 统计数据
    total_equipments = Equipment.query.count()
    total_plans = MaintenancePlan.query.count()
    total_records = MaintenanceRecord.query.count()
    total_faults = FaultRecord.query.count()
    
    # 待维护设备数
    today = datetime.utcnow().date()
    pending_maintenance = MaintenancePlan.query.filter(MaintenancePlan.next_maintenance_date <= today).count()
    
    # 最近维护记录
    recent_records = MaintenanceRecord.query.order_by(MaintenanceRecord.maintenance_date.desc()).limit(5).all()
    
    # 最近故障记录
    recent_faults = FaultRecord.query.order_by(FaultRecord.occurrence_time.desc()).limit(5).all()
    
    return render_template('analytical_maintenance/dashboard.html',
                          total_equipments=total_equipments,
                          total_plans=total_plans,
                          total_records=total_records,
                          total_faults=total_faults,
                          pending_maintenance=pending_maintenance,
                          recent_records=recent_records,
                          recent_faults=recent_faults)

# 仪表列表
@analytical_maintenance_bp.route('/equipment/')
def equipment_index():
    """仪表列表"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    per_page = 10
    
    # 构建查询
    query = Equipment.query
    
    # 添加搜索条件
    if search:
        query = query.filter(
            (Equipment.name.ilike(f'%{search}%')) | 
            (Equipment.equipment_number.ilike(f'%{search}%'))
        )
    
    # 按创建时间倒序排列
    pagination = query.order_by(Equipment.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    equipments = pagination.items
    
    # 获取当前日期
    today = datetime.utcnow().date()
    
    return render_template('analytical_maintenance/equipment_index.html',
                          equipments=equipments,
                          pagination=pagination,
                          today=today,
                          search=search)

# 添加仪表
@analytical_maintenance_bp.route('/equipment/add/', methods=['GET', 'POST'])
def equipment_add():
    """添加仪表"""
    if request.method == 'POST':
        # 获取表单数据
        equipment_number = request.form['equipment_number']
        name = request.form['name']
        model = request.form['model']
        specification = request.form['specification']
        location = request.form['location']
        measurement_parameter = request.form['measurement_parameter']
        serial_number = request.form['serial_number']
        responsible_person = request.form['responsible_person']
        
        # 处理日期字段
        purchase_date_str = request.form.get('purchase_date')
        purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date() if purchase_date_str else None
        
        # 创建新仪表
        new_equipment = Equipment(
            equipment_number=equipment_number,
            name=name,
            model=model,
            specification=specification,
            location=location,
            serial_number=serial_number,
            responsible_person=responsible_person,
            purchase_date=purchase_date,
            status='in_use',  # 默认状态为在用
            specs_json={'measurement_parameter': measurement_parameter} if measurement_parameter else None
        )
        
        # 保存到数据库
        db.session.add(new_equipment)
        db.session.commit()
        
        flash('仪表添加成功！', 'success')
        return redirect(url_for('analytical_maintenance.equipment_index'))
    
    return render_template('analytical_maintenance/equipment_add.html')

# 删除仪表
@analytical_maintenance_bp.route('/equipment/delete/<int:id>/', methods=['POST'])
def equipment_delete(id):
    """删除分析仪表"""
    # 获取仪表
    equipment = Equipment.query.get_or_404(id)
    
    # 删除仪表
    db.session.delete(equipment)
    db.session.commit()
    
    flash('仪表删除成功！', 'success')
    return redirect(url_for('analytical_maintenance.equipment_index'))

# 维护计划列表
@analytical_maintenance_bp.route('/plan/')
def plan_index():
    """维护计划列表"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    equipment_id = request.args.get('equipment_id', type=int)
    per_page = 10
    
    # 构建查询
    if equipment_id:
        query = MaintenancePlan.query.filter_by(equipment_id=equipment_id)
    else:
        query = MaintenancePlan.query
    
    # 按下次维护日期排序
    pagination = query.order_by(MaintenancePlan.next_maintenance_date).paginate(page=page, per_page=per_page, error_out=False)
    plans = pagination.items
    
    # 获取所有设备
    equipments = Equipment.query.all()
    
    # 获取当前日期
    today = datetime.utcnow().date()
    
    return render_template('analytical_maintenance/plan_index.html',
                          plans=plans,
                          pagination=pagination,
                          selected_equipment=equipment_id,
                          equipments=equipments,
                          today=today)

# 添加维护计划
@analytical_maintenance_bp.route('/plan/add/', methods=['GET', 'POST'])
def plan_add():
    """添加维护计划"""
    # 获取所有设备
    equipments = Equipment.query.all()
    
    if request.method == 'POST':
        # 获取表单数据
        equipment_id = request.form['equipment_id']
        plan_name = request.form['plan_name']
        description = request.form.get('description')
        maintenance_type = request.form['maintenance_type']
        frequency = request.form['frequency']
        next_maintenance_date = datetime.strptime(request.form['next_maintenance_date'], '%Y-%m-%d').date()
        created_by = request.form['created_by']
        
        # 创建新维护计划
        new_plan = MaintenancePlan(
            equipment_id=equipment_id,
            plan_name=plan_name,
            description=description,
            maintenance_type=maintenance_type,
            frequency=frequency,
            next_maintenance_date=next_maintenance_date,
            created_by=created_by
        )
        
        # 保存到数据库
        db.session.add(new_plan)
        db.session.commit()
        
        flash('维护计划添加成功！', 'success')
        return redirect(url_for('analytical_maintenance.plan_index'))
    
    return render_template('analytical_maintenance/plan_add.html', equipments=equipments)

# 编辑维护计划
@analytical_maintenance_bp.route('/plan/edit/<int:id>/', methods=['GET', 'POST'])
def plan_edit(id):
    """编辑维护计划"""
    # 获取维护计划
    plan = MaintenancePlan.query.get_or_404(id)
    
    # 获取所有设备
    equipments = Equipment.query.all()
    
    if request.method == 'POST':
        # 获取表单数据
        plan.equipment_id = request.form['equipment_id']
        plan.plan_name = request.form['plan_name']
        plan.description = request.form.get('description')
        plan.maintenance_type = request.form['maintenance_type']
        plan.frequency = request.form['frequency']
        plan.next_maintenance_date = datetime.strptime(request.form['next_maintenance_date'], '%Y-%m-%d').date()
        plan.created_by = request.form['created_by']
        
        # 保存到数据库
        db.session.commit()
        
        flash('维护计划编辑成功！', 'success')
        return redirect(url_for('analytical_maintenance.plan_index'))
    
    return render_template('analytical_maintenance/plan_edit.html', plan=plan, equipments=equipments)

# 删除维护计划
@analytical_maintenance_bp.route('/plan/delete/<int:id>/', methods=['POST'])
def plan_delete(id):
    """删除维护计划"""
    # 获取维护计划
    plan = MaintenancePlan.query.get_or_404(id)
    
    # 删除维护计划
    db.session.delete(plan)
    db.session.commit()
    
    flash('维护计划删除成功！', 'success')
    return redirect(url_for('analytical_maintenance.plan_index'))

# 维护记录列表
@analytical_maintenance_bp.route('/record/')
def record_index():
    """维护记录列表"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    plan_id = request.args.get('plan_id', type=int)
    equipment_id = request.args.get('equipment_id', type=int)
    per_page = 10
    
    # 构建查询
    query = MaintenanceRecord.query
    
    if plan_id:
        query = query.filter_by(plan_id=plan_id)
    
    if equipment_id:
        query = query.filter_by(equipment_id=equipment_id)
    
    # 按维护日期倒序排列
    pagination = query.order_by(MaintenanceRecord.maintenance_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    records = pagination.items
    
    # 获取所有计划和设备
    plans = MaintenancePlan.query.all()
    equipments = Equipment.query.all()
    
    return render_template('analytical_maintenance/record_index.html',
                          records=records,
                          pagination=pagination,
                          selected_plan=plan_id,
                          selected_equipment=equipment_id,
                          plans=plans,
                          equipments=equipments)

# 添加维护记录
@analytical_maintenance_bp.route('/record/add/', methods=['GET', 'POST'])
def record_add():
    """添加维护记录"""
    # 获取所有计划和设备
    plans = MaintenancePlan.query.all()
    equipments = Equipment.query.all()
    
    if request.method == 'POST':
        # 获取表单数据
        plan_id = request.form['plan_id']
        equipment_id = request.form['equipment_id']
        maintenance_date = datetime.strptime(request.form['maintenance_date'], '%Y-%m-%d').date()
        executor = request.form['executor']
        content = request.form['content']
        result = request.form['result']
        notes = request.form.get('notes')
        spare_parts_used = request.form.get('spare_parts_used')
        maintenance_cost = request.form.get('maintenance_cost')
        
        # 创建新维护记录
        new_record = MaintenanceRecord(
            plan_id=plan_id,
            equipment_id=equipment_id,
            maintenance_date=maintenance_date,
            executor=executor,
            content=content,
            result=result,
            notes=notes,
            spare_parts_used=spare_parts_used,
            maintenance_cost=float(maintenance_cost) if maintenance_cost else None
        )
        
        # 保存到数据库
        db.session.add(new_record)
        
        # 更新设备维护信息
        equipment = Equipment.query.get_or_404(equipment_id)
        equipment.last_maintenance_date = maintenance_date
        
        # 更新维护计划下次维护日期
        plan = MaintenancePlan.query.get_or_404(plan_id)
        from datetime import timedelta
        if plan.frequency == 'daily':
            next_date = maintenance_date + timedelta(days=1)
        elif plan.frequency == 'weekly':
            next_date = maintenance_date + timedelta(weeks=1)
        elif plan.frequency == 'monthly':
            next_date = maintenance_date + timedelta(days=30)
        elif plan.frequency == 'quarterly':
            next_date = maintenance_date + timedelta(days=90)
        elif plan.frequency == 'yearly':
            next_date = maintenance_date + timedelta(days=365)
        else:
            next_date = maintenance_date + timedelta(days=30)
        
        plan.next_maintenance_date = next_date
        equipment.next_maintenance_date = next_date
        
        # 保存到数据库
        db.session.commit()
        
        flash('维护记录添加成功！', 'success')
        return redirect(url_for('analytical_maintenance.record_index'))
    
    return render_template('analytical_maintenance/record_add.html', plans=plans, equipments=equipments)

# 故障记录列表
@analytical_maintenance_bp.route('/fault/')
def fault_index():
    """故障记录列表"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    equipment_id = request.args.get('equipment_id', type=int)
    per_page = 10
    
    # 构建查询
    query = FaultRecord.query
    
    if equipment_id:
        query = query.filter_by(equipment_id=equipment_id)
    
    # 按故障发生时间倒序排列
    pagination = query.order_by(FaultRecord.occurrence_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    faults = pagination.items
    
    # 获取所有设备
    equipments = Equipment.query.all()
    
    return render_template('analytical_maintenance/fault_index.html',
                          faults=faults,
                          pagination=pagination,
                          selected_equipment=equipment_id,
                          equipments=equipments)

# 添加故障记录
@analytical_maintenance_bp.route('/fault/add/', methods=['GET', 'POST'])
def fault_add():
    """添加故障记录"""
    # 获取所有设备
    equipments = Equipment.query.all()
    
    if request.method == 'POST':
        # 获取表单数据
        equipment_id = request.form['equipment_id']
        fault_phenomenon = request.form['fault_phenomenon']
        # 处理时间格式，将 'T' 替换为空格，并添加秒数
        occurrence_time_str = request.form['occurrence_time']
        if 'T' in occurrence_time_str:
            # 将 '2025-12-23T07:57' 转换为 '2025-12-23 07:57:00'
            occurrence_time_str = occurrence_time_str.replace('T', ' ') + ':00'
        occurrence_time = datetime.strptime(occurrence_time_str, '%Y-%m-%d %H:%M:%S')
        reporter = request.form['reporter']
        fault_type = request.form.get('fault_type')
        impact_level = request.form.get('impact_level')
        urgency_level = request.form.get('urgency_level')
        
        # 创建新故障记录
        new_fault = FaultRecord(
            equipment_id=equipment_id,
            fault_phenomenon=fault_phenomenon,
            occurrence_time=occurrence_time,
            reporter=reporter,
            fault_type=fault_type,
            impact_level=impact_level,
            urgency_level=urgency_level
        )
        
        # 保存到数据库
        db.session.add(new_fault)
        db.session.commit()
        
        flash('故障记录添加成功！', 'success')
        return redirect(url_for('analytical_maintenance.fault_index'))
    
    # 获取当前时间
    now = datetime.utcnow()
    return render_template('analytical_maintenance/fault_add.html', equipments=equipments, now=now)

# 故障详情
@analytical_maintenance_bp.route('/fault/detail/<int:id>/')
def fault_detail(id):
    """故障详情"""
    # 获取故障记录
    fault = FaultRecord.query.get_or_404(id)
    
    return render_template('analytical_maintenance/fault_detail.html', fault=fault)

# 添加故障解决方案
@analytical_maintenance_bp.route('/fault/solution/add/<int:fault_id>/', methods=['GET', 'POST'])
def fault_solution_add(fault_id):
    """添加故障解决方案"""
    # 获取故障记录
    fault = FaultRecord.query.get_or_404(fault_id)
    
    if request.method == 'POST':
        # 获取表单数据
        handler = request.form['handler']
        start_time = datetime.strptime(request.form['start_time'], '%Y-%m-%d %H:%M:%S')
        end_time = request.form['end_time']
        process_description = request.form['process_description']
        solution = request.form['solution']
        verification_result = request.form['verification_result']
        notes = request.form.get('notes')
        spare_parts_used = request.form.get('spare_parts_used')
        repair_cost = request.form.get('repair_cost')
        
        # 处理结束时间
        end_time_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S') if end_time else None
        
        # 创建新故障解决方案
        new_solution = FaultSolution(
            fault_id=fault_id,
            handler=handler,
            start_time=start_time,
            end_time=end_time_dt,
            process_description=process_description,
            solution=solution,
            verification_result=verification_result,
            notes=notes,
            spare_parts_used=spare_parts_used,
            repair_cost=float(repair_cost) if repair_cost else None
        )
        
        # 保存到数据库
        db.session.add(new_solution)
        
        # 更新故障状态
        fault.status = 'resolved'
        
        # 保存到数据库
        db.session.commit()
        
        flash('故障解决方案添加成功！', 'success')
        return redirect(url_for('analytical_maintenance.fault_detail', id=fault_id))
    
    # 获取当前时间
    now = datetime.utcnow()
    return render_template('analytical_maintenance/fault_solution_add.html', fault=fault, now=now)
