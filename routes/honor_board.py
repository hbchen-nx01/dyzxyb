from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from models import db, HonorBoard
from datetime import datetime
import os
import uuid
import subprocess

# 创建蓝图
honor_board_bp = Blueprint('honor_board', __name__)

# 检查文件是否允许上传
def allowed_file(filename):
    from app import app
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@honor_board_bp.route('/')
def honor_board_index():
    """光荣榜首页，支持查询"""
    # 获取查询参数
    employee_name = request.args.get('employee_name', '')
    award_type = request.args.get('award_type', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # 构建查询
    query = HonorBoard.query
    
    # 按人员姓名查询
    if employee_name:
        query = query.filter(HonorBoard.employee_name.like(f'%{employee_name}%'))
    
    # 按奖励类型查询
    if award_type:
        query = query.filter(HonorBoard.award_type.like(f'%{award_type}%'))
    
    # 按时间范围查询
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        query = query.filter(HonorBoard.award_date >= start_date_obj)
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(HonorBoard.award_date <= end_date_obj)
    
    # 按获得时间倒序排列
    honor_list = query.order_by(HonorBoard.award_date.desc()).all()
    
    return render_template('honor_board/index.html', honor_list=honor_list)

@honor_board_bp.route('/add', methods=['GET', 'POST'])
def add_honor():
    """添加光荣榜条目"""
    if request.method == 'POST':
        # 获取表单数据
        employee_name = request.form['employee_name']
        award_type = request.form['award_type']
        award_content = request.form['award_content']
        award_date = request.form['award_date']
        
        # 处理图片上传
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                # 生成唯一文件名
                filename = f"{uuid.uuid4()}_{file.filename}"
                from app import app
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = filename
        
        # 创建新条目
        new_honor = HonorBoard(
            employee_name=employee_name,
            award_type=award_type,
            award_content=award_content,
            award_date=datetime.strptime(award_date, '%Y-%m-%d').date(),
            image_path=image_path
        )
        
        # 保存到数据库
        db.session.add(new_honor)
        db.session.commit()
        
        flash('光荣榜条目添加成功！', 'success')
        return redirect(url_for('honor_board.honor_board_index'))
    
    return render_template('honor_board/add.html')

@honor_board_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_honor(id):
    """编辑光荣榜条目"""
    honor = HonorBoard.query.get_or_404(id)
    
    if request.method == 'POST':
        # 获取表单数据
        honor.employee_name = request.form['employee_name']
        honor.award_type = request.form['award_type']
        honor.award_content = request.form['award_content']
        honor.award_date = datetime.strptime(request.form['award_date'], '%Y-%m-%d').date()
        
        # 处理图片上传
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                # 删除旧图片
                if honor.image_path:
                    from app import app
                    old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], honor.image_path)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                # 保存新图片
                filename = f"{uuid.uuid4()}_{file.filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                honor.image_path = filename
        
        # 保存到数据库
        db.session.commit()
        
        flash('光荣榜条目编辑成功！', 'success')
        return redirect(url_for('honor_board.honor_board_index'))
    
    return render_template('honor_board/edit.html', honor=honor)

@honor_board_bp.route('/delete/<int:id>', methods=['POST'])
def delete_honor(id):
    """删除光荣榜条目"""
    honor = HonorBoard.query.get_or_404(id)
    
    # 删除图片文件
    if honor.image_path:
        from app import app
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], honor.image_path)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # 删除数据库记录
    db.session.delete(honor)
    db.session.commit()
    
    flash('光荣榜条目删除成功！', 'success')
    return redirect(url_for('honor_board.honor_board_index'))

@honor_board_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传文件的访问"""
    from app import app
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@honor_board_bp.route('/open-image-folder')
def open_image_folder():
    """打开图片文件夹"""
    from app import app
    folder_path = app.config['UPLOAD_FOLDER_ABSOLUTE']
    
    try:
        # 根据操作系统打开文件夹
        if os.name == 'nt':  # Windows
            subprocess.Popen(f'explorer "{folder_path}"')
        elif os.name == 'posix':  # macOS or Linux
            subprocess.Popen(['open', folder_path])
        
        flash('图片文件夹已打开！', 'success')
    except Exception as e:
        flash(f'打开图片文件夹失败：{str(e)}', 'error')
    
    return redirect(url_for('honor_board.honor_board_index'))
