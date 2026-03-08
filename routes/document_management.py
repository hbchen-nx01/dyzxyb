from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from models import db, Document, DocumentCategory
from datetime import datetime
import os
import uuid
import subprocess

# 创建蓝图
document_management_bp = Blueprint('document_management', __name__)

# 检查文件是否允许上传
def allowed_file(filename):
    from app import app
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@document_management_bp.route('/')
def document_management_index():
    """文档管理首页，支持查询"""
    # 获取查询参数
    title = request.args.get('title', '')
    category_id = request.args.get('category_id', '')
    uploader = request.args.get('uploader', '')
    
    # 构建查询
    query = Document.query
    
    # 按标题查询
    if title:
        query = query.filter(Document.title.like(f'%{title}%'))
    
    # 按分类查询
    if category_id:
        query = query.filter(Document.category_id == int(category_id))
    
    # 按上传人查询
    if uploader:
        query = query.filter(Document.uploader.like(f'%{uploader}%'))
    
    # 获取所有分类
    categories = DocumentCategory.query.all()
    
    # 按上传时间倒序排列
    documents = query.order_by(Document.upload_date.desc()).all()
    
    return render_template('document_management/index.html', documents=documents, categories=categories)

@document_management_bp.route('/add', methods=['GET', 'POST'])
def add_document():
    """上传文档"""
    # 获取所有分类
    categories = DocumentCategory.query.all()
    
    if request.method == 'POST':
        # 获取表单数据
        title = request.form['title']
        category_id = request.form['category_id']
        uploader = request.form['uploader']
        
        # 处理文件上传
        if 'document' not in request.files:
            flash('未选择文件', 'error')
            return redirect(request.url)
        
        file = request.files['document']
        if file.filename == '':
            flash('未选择文件', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # 生成唯一文件名
            filename = f"{uuid.uuid4()}_{file.filename}"
            from app import app
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # 保存文件
            file.save(file_path)
            
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            
            # 创建新文档记录
            new_document = Document(
                title=title,
                category_id=category_id,
                file_path=filename,
                file_name=file.filename,
                file_size=file_size,
                uploader=uploader
            )
            
            # 保存到数据库
            db.session.add(new_document)
            db.session.commit()
            
            flash('文档上传成功！', 'success')
            return redirect(url_for('document_management.document_management_index'))
        else:
            flash('不允许的文件类型', 'error')
            return redirect(request.url)
    
    return render_template('document_management/add.html', categories=categories)

@document_management_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_document(id):
    """编辑文档信息"""
    document = Document.query.get_or_404(id)
    categories = DocumentCategory.query.all()
    
    if request.method == 'POST':
        # 更新文档信息
        document.title = request.form['title']
        document.category_id = request.form['category_id']
        document.uploader = request.form['uploader']
        
        # 保存到数据库
        db.session.commit()
        
        flash('文档信息更新成功！', 'success')
        return redirect(url_for('document_management.document_management_index'))
    
    return render_template('document_management/edit.html', document=document, categories=categories)

@document_management_bp.route('/delete/<int:id>', methods=['POST'])
def delete_document(id):
    """删除文档"""
    document = Document.query.get_or_404(id)
    
    # 删除文件
    from app import app
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], document.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 删除数据库记录
    db.session.delete(document)
    db.session.commit()
    
    flash('文档删除成功！', 'success')
    return redirect(url_for('document_management.document_management_index'))

@document_management_bp.route('/download/<int:id>')
def download_document(id):
    """下载文档"""
    document = Document.query.get_or_404(id)
    from app import app
    return send_from_directory(app.config['UPLOAD_FOLDER'], document.file_path, as_attachment=True, attachment_filename=document.file_name)
