from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Equipment, RepairRecycle
from datetime import datetime
import os
from werkzeug.utils import secure_filename

# 创建蓝图
repair_recycle_bp = Blueprint('repair_recycle', __name__)

# 允许的图片扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 修旧利废记录列表页
@repair_recycle_bp.route('/')
def repair_recycle_index():
    """修旧利废记录列表页"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    equipment_name = request.args.get('equipment_name')
    repair_person = request.args.get('repair_person')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    per_page = 10
    
    # 构建查询
    query = RepairRecycle.query
    
    if equipment_name:
        query = query.filter(RepairRecycle.equipment_name.like(f'%{equipment_name}%'))
    
    if repair_person:
        query = query.filter(RepairRecycle.repair_person.like(f'%{repair_person}%'))
    
    # 新增：按项目名称查询
    project_name = request.args.get('project_name')
    if project_name:
        query = query.filter(RepairRecycle.project_name.like(f'%{project_name}%'))
    
    if start_date:
        query = query.filter(RepairRecycle.repair_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    
    if end_date:
        query = query.filter(RepairRecycle.repair_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    # 按修复日期倒序排列
    pagination = query.order_by(RepairRecycle.repair_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    records = pagination.items
    
    # 获取所有设备
    equipments = Equipment.query.all()
    
    # 获取所有修复人员
    repair_persons = db.session.query(RepairRecycle.repair_person).distinct().all()
    repair_person_list = [person[0] for person in repair_persons if person[0]]
    
    return render_template('repair_recycle/index.html', 
                          records=records, 
                          pagination=pagination,
                          selected_equipment_name=equipment_name,
                          selected_person=repair_person,
                          selected_start_date=start_date,
                          selected_end_date=end_date,
                          project_name=project_name,
                          equipments=equipments,
                          repair_person_list=repair_person_list)

# 添加修旧利废记录页面
@repair_recycle_bp.route('/add/', methods=['GET', 'POST'])
def add_repair_recycle():
    """添加修旧利废记录页面"""
    if request.method == 'POST':
        # 获取表单数据
        equipment_name = request.form['equipment_name']
        project_name = request.form['project_name']
        repair_date_str = request.form['repair_date']
        repair_person = request.form['repair_person']
        before_status = request.form['before_status']
        after_status = request.form['after_status']
        before_value = float(request.form['before_value'])
        after_value = float(request.form['after_value'])
        description = request.form.get('description')
        
        # 转换日期
        repair_date = datetime.strptime(repair_date_str, '%Y-%m-%d').date()
        
        # 处理图片上传
        before_image_path = None
        after_image_path = None
        
        # 确保uploads目录存在
        upload_folder = os.path.join(os.getcwd(), 'static', 'uploads', 'repair_recycle')
        os.makedirs(upload_folder, exist_ok=True)
        
        # 上传修复前图片
        if 'before_image' in request.files:
            before_file = request.files['before_image']
            if before_file and allowed_file(before_file.filename):
                filename = secure_filename(f"before_{datetime.now().strftime('%Y%m%d%H%M%S')}_{before_file.filename}")
                file_path = os.path.join(upload_folder, filename)
                before_file.save(file_path)
                before_image_path = f"uploads/repair_recycle/{filename}"
        
        # 上传修复后图片
        if 'after_image' in request.files:
            after_file = request.files['after_image']
            if after_file and allowed_file(after_file.filename):
                filename = secure_filename(f"after_{datetime.now().strftime('%Y%m%d%H%M%S')}_{after_file.filename}")
                file_path = os.path.join(upload_folder, filename)
                after_file.save(file_path)
                after_image_path = f"uploads/repair_recycle/{filename}"
        
        # 创建新记录
        new_record = RepairRecycle(
            equipment_name=equipment_name,
            project_name=project_name,
            repair_date=repair_date,
            repair_person=repair_person,
            before_status=before_status,
            after_status=after_status,
            before_value=before_value,
            after_value=after_value,
            before_image_path=before_image_path,
            after_image_path=after_image_path,
            description=description
        )
        
        # 保存到数据库
        db.session.add(new_record)
        db.session.commit()
        
        flash('修旧利废记录添加成功！', 'success')
        return redirect(url_for('repair_recycle.repair_recycle_index'))
    
    return render_template('repair_recycle/add.html')

# 编辑修旧利废记录页面
@repair_recycle_bp.route('/edit/<int:id>/', methods=['GET', 'POST'])
def edit_repair_recycle(id):
    """编辑修旧利废记录页面"""
    # 获取记录
    record = RepairRecycle.query.get_or_404(id)
    
    if request.method == 'POST':
        # 获取表单数据
        record.equipment_name = request.form['equipment_name']
        record.project_name = request.form['project_name']
        record.repair_date = datetime.strptime(request.form['repair_date'], '%Y-%m-%d').date()
        record.repair_person = request.form['repair_person']
        record.before_status = request.form['before_status']
        record.after_status = request.form['after_status']
        record.before_value = float(request.form['before_value'])
        record.after_value = float(request.form['after_value'])
        record.description = request.form.get('description')
        
        # 处理图片上传
        upload_folder = os.path.join(os.getcwd(), 'static', 'uploads', 'repair_recycle')
        os.makedirs(upload_folder, exist_ok=True)
        
        # 上传修复前图片
        if 'before_image' in request.files:
            before_file = request.files['before_image']
            if before_file and allowed_file(before_file.filename):
                # 删除旧图片
                if record.before_image_path:
                    old_path = os.path.join(os.getcwd(), 'static', record.before_image_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                # 保存新图片
                filename = secure_filename(f"before_{datetime.now().strftime('%Y%m%d%H%M%S')}_{before_file.filename}")
                file_path = os.path.join(upload_folder, filename)
                before_file.save(file_path)
                record.before_image_path = f"uploads/repair_recycle/{filename}"
        
        # 上传修复后图片
        if 'after_image' in request.files:
            after_file = request.files['after_image']
            if after_file and allowed_file(after_file.filename):
                # 删除旧图片
                if record.after_image_path:
                    old_path = os.path.join(os.getcwd(), 'static', record.after_image_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                # 保存新图片
                filename = secure_filename(f"after_{datetime.now().strftime('%Y%m%d%H%M%S')}_{after_file.filename}")
                file_path = os.path.join(upload_folder, filename)
                after_file.save(file_path)
                record.after_image_path = f"uploads/repair_recycle/{filename}"
        
        # 保存到数据库
        db.session.commit()
        
        flash('修旧利废记录编辑成功！', 'success')
        return redirect(url_for('repair_recycle.repair_recycle_index'))
    
    return render_template('repair_recycle/edit.html', record=record)

# 删除修旧利废记录
@repair_recycle_bp.route('/delete/<int:id>/', methods=['POST'])
def delete_repair_recycle(id):
    """删除修旧利废记录"""
    # 获取记录
    record = RepairRecycle.query.get_or_404(id)
    
    # 删除图片文件
    if record.before_image_path:
        before_path = os.path.join(os.getcwd(), 'static', record.before_image_path)
        if os.path.exists(before_path):
            os.remove(before_path)
    
    if record.after_image_path:
        after_path = os.path.join(os.getcwd(), 'static', record.after_image_path)
        if os.path.exists(after_path):
            os.remove(after_path)
    
    # 删除记录
    db.session.delete(record)
    db.session.commit()
    
    flash('修旧利废记录删除成功！', 'success')
    return redirect(url_for('repair_recycle.repair_recycle_index'))

# 修旧利废记录详情页
@repair_recycle_bp.route('/detail/<int:id>/')
def repair_recycle_detail(id):
    """修旧利废记录详情页"""
    # 获取记录
    record = RepairRecycle.query.get_or_404(id)
    
    return render_template('repair_recycle/detail.html', record=record)

# 修旧利废统计分析页
@repair_recycle_bp.route('/statistics/')
def repair_recycle_statistics():
    """修旧利废统计分析页"""
    # 总记录数
    total_records = RepairRecycle.query.count()
    
    # 总效益
    total_benefit = db.session.query(db.func.sum(RepairRecycle.after_value - RepairRecycle.before_value)).scalar() or 0
    
    # 按设备统计
    equipment_benefits = db.session.query(
        RepairRecycle.equipment_name,
        db.func.count(RepairRecycle.id),
        db.func.sum(RepairRecycle.after_value - RepairRecycle.before_value)
    ).group_by(RepairRecycle.equipment_name).all()
    
    # 按月份统计
    month_benefits = db.session.query(
        db.func.strftime('%Y-%m', RepairRecycle.repair_date),
        db.func.count(RepairRecycle.id),
        db.func.sum(RepairRecycle.after_value - RepairRecycle.before_value)
    ).group_by(db.func.strftime('%Y-%m', RepairRecycle.repair_date)).order_by(db.func.strftime('%Y-%m', RepairRecycle.repair_date)).all()
    
    # 按修复人员统计
    person_benefits = db.session.query(
        RepairRecycle.repair_person,
        db.func.count(RepairRecycle.id),
        db.func.sum(RepairRecycle.after_value - RepairRecycle.before_value)
    ).group_by(RepairRecycle.repair_person).all()
    
    # 按设备分类统计（已移除，因为设备名称改为手动输入）
    
    # 新增：按年度统计
    year_benefits = db.session.query(
        db.func.strftime('%Y', RepairRecycle.repair_date),
        db.func.count(RepairRecycle.id),
        db.func.sum(RepairRecycle.after_value - RepairRecycle.before_value)
    ).group_by(db.func.strftime('%Y', RepairRecycle.repair_date)).order_by(db.func.strftime('%Y', RepairRecycle.repair_date)).all()
    
    return render_template('repair_recycle/statistics.html',
                          total_records=total_records,
                          total_benefit=total_benefit,
                          equipment_benefits=equipment_benefits,
                          month_benefits=month_benefits,
                          person_benefits=person_benefits,
                          year_benefits=year_benefits)