from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from models import db, ArticleCategory, Article, ArticleMedia, Comment, Like
from datetime import datetime
import os
import uuid
import subprocess

# 创建蓝图
experience_bp = Blueprint('experience', __name__)

# 经验分享首页
@experience_bp.route('/')
def experience_index():
    """经验分享首页，显示文章列表"""
    # 获取查询参数
    category_id = request.args.get('category_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 构建查询
    if category_id:
        query = Article.query.filter_by(category_id=category_id)
    else:
        query = Article.query
    
    # 按创建时间倒序排列
    pagination = query.order_by(Article.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    articles = pagination.items
    
    # 获取所有分类
    categories = ArticleCategory.query.all()
    
    return render_template('experience/index.html', articles=articles, categories=categories, pagination=pagination, selected_category=category_id)

# 按分类显示文章
@experience_bp.route('/category/<int:category_id>/')
def experience_category(category_id):
    """按分类显示文章"""
    # 重定向到首页，并传递分类ID参数
    return redirect(url_for('experience.experience_index', category_id=category_id))

# 文章详情页
@experience_bp.route('/article/<int:id>/')
def article_detail(id):
    """文章详情页"""
    # 获取文章
    article = Article.query.get_or_404(id)
    
    # 增加浏览次数
    article.views += 1
    db.session.commit()
    
    # 获取评论
    comments = article.comments
    
    return render_template('experience/article.html', article=article, comments=comments)

# 添加文章/分享页面
@experience_bp.route('/add/', methods=['GET', 'POST'])
def add_article():
    """添加文章或分享"""
    # 获取所有分类
    categories = ArticleCategory.query.all()
    
    if request.method == 'POST':
        # 获取表单数据
        type = request.form.get('type', 'article')
        title = request.form.get('title')  # 短分享可以没有标题
        content = request.form['content']
        category_id = request.form['category_id']
        author = request.form['author']
        
        # 创建新文章/分享
        new_article = Article(
            type=type,
            title=title,
            content=content,
            category_id=category_id,
            author=author
        )
        
        # 保存到数据库
        db.session.add(new_article)
        db.session.commit()
        
        # 处理多媒体文件上传
        if 'media' in request.files:
            files = request.files.getlist('media')
            for file in files:
                if file.filename != '':
                    # 生成唯一文件名
                    filename = f"{uuid.uuid4()}_{file.filename}"
                    # 确定文件类型
                    file_type = 'image' if file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'video'
                    # 保存文件
                    file.save(os.path.join('static', 'uploads', 'experience', filename))
                    # 创建媒体记录
                    new_media = ArticleMedia(
                        article_id=new_article.id,
                        file_path=filename,
                        file_type=file_type
                    )
                    db.session.add(new_media)
            # 提交媒体记录
            db.session.commit()
        
        flash(f'{"分享" if type == "share" else "文章"}发布成功！', 'success')
        return redirect(url_for('experience.article_detail', id=new_article.id))
    
    return render_template('experience/add.html', categories=categories)

# 快速分享路由
@experience_bp.route('/quick-share/', methods=['POST'])
def quick_share():
    """快速分享功能"""
    # 获取表单数据
    content = request.form.get('content')
    category_id = request.form.get('category_id')
    author = request.form.get('author', '匿名用户')
    
    if not content or not category_id:
        flash('分享内容和分类不能为空！', 'danger')
        return redirect(url_for('experience.experience_index'))
    
    # 创建新分享
    new_share = Article(
        type='share',
        content=content,
        category_id=category_id,
        author=author
    )
    
    # 保存到数据库
    db.session.add(new_share)
    db.session.commit()
    
    # 处理多媒体文件上传
    if 'media' in request.files:
        files = request.files.getlist('media')
        for file in files:
            if file.filename != '':
                # 生成唯一文件名
                filename = f"{uuid.uuid4()}_{file.filename}"
                # 确定文件类型
                file_type = 'image' if file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'video'
                # 保存文件
                file.save(os.path.join('static', 'uploads', 'experience', filename))
                # 创建媒体记录
                new_media = ArticleMedia(
                    article_id=new_share.id,
                    file_path=filename,
                    file_type=file_type
                )
                db.session.add(new_media)
        # 提交媒体记录
        db.session.commit()
    
    flash('分享发布成功！', 'success')
    return redirect(url_for('experience.experience_index'))

# 编辑文章/分享页面
@experience_bp.route('/edit/<int:id>/', methods=['GET', 'POST'])
def edit_article(id):
    """编辑文章或分享"""
    # 获取文章
    article = Article.query.get_or_404(id)
    
    # 获取所有分类
    categories = ArticleCategory.query.all()
    
    if request.method == 'POST':
        # 获取表单数据
        article.type = request.form.get('type', 'article')
        article.title = request.form.get('title')  # 短分享可以没有标题
        article.content = request.form['content']
        article.category_id = request.form['category_id']
        article.author = request.form['author']
        
        # 保存到数据库
        db.session.commit()
        
        # 处理新上传的多媒体文件
        if 'media' in request.files:
            files = request.files.getlist('media')
            for file in files:
                if file.filename != '':
                    # 生成唯一文件名
                    filename = f"{uuid.uuid4()}_{file.filename}"
                    # 确定文件类型
                    file_type = 'image' if file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'video'
                    # 保存文件
                    file.save(os.path.join('static', 'uploads', 'experience', filename))
                    # 创建媒体记录
                    new_media = ArticleMedia(
                        article_id=article.id,
                        file_path=filename,
                        file_type=file_type
                    )
                    db.session.add(new_media)
            # 提交媒体记录
            db.session.commit()
        
        flash(f'{"分享" if article.type == "share" else "文章"}编辑成功！', 'success')
        return redirect(url_for('experience.article_detail', id=article.id))
    
    return render_template('experience/edit.html', article=article, categories=categories)

# 删除文章
@experience_bp.route('/delete/<int:id>/', methods=['POST'])
def delete_article(id):
    """删除文章"""
    # 获取文章
    article = Article.query.get_or_404(id)
    
    # 删除关联的媒体文件
    for media in article.media:
        # 删除文件
        file_path = os.path.join('static', 'uploads', 'experience', media.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # 删除文章
    db.session.delete(article)
    db.session.commit()
    
    flash('文章删除成功！', 'success')
    return redirect(url_for('experience.experience_index'))

# 删除文章媒体
@experience_bp.route('/media/delete/<int:id>/', methods=['POST'])
def delete_media(id):
    """删除文章媒体"""
    # 获取媒体
    media = ArticleMedia.query.get_or_404(id)
    article_id = media.article_id
    
    # 删除文件
    file_path = os.path.join('static', 'uploads', 'experience', media.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 删除媒体记录
    db.session.delete(media)
    db.session.commit()
    
    flash('媒体文件删除成功！', 'success')
    return redirect(url_for('experience.edit_article', id=article_id))

# 添加评论
@experience_bp.route('/article/<int:id>/comment/', methods=['POST'])
def add_comment(id):
    """添加评论"""
    # 获取文章
    article = Article.query.get_or_404(id)
    
    # 获取表单数据
    content = request.form['content']
    author = request.form['author']
    
    # 创建新评论
    new_comment = Comment(
        article_id=id,
        content=content,
        author=author
    )
    
    # 保存到数据库
    db.session.add(new_comment)
    db.session.commit()
    
    flash('评论添加成功！', 'success')
    return redirect(url_for('experience.article_detail', id=id))

# 删除评论
@experience_bp.route('/comment/delete/<int:id>/', methods=['POST'])
def delete_comment(id):
    """删除评论"""
    # 获取评论
    comment = Comment.query.get_or_404(id)
    article_id = comment.article_id
    
    # 删除评论
    db.session.delete(comment)
    db.session.commit()
    
    flash('评论删除成功！', 'success')
    return redirect(url_for('experience.article_detail', id=article_id))

# 点赞/取消点赞
@experience_bp.route('/article/<int:id>/like/', methods=['POST'])
def like_article(id):
    """点赞/取消点赞"""
    # 获取文章
    article = Article.query.get_or_404(id)
    
    # 获取点赞用户（这里使用固定用户名，实际应用中应该从登录信息获取）
    user = '匿名用户'  # 实际应用中应该替换为登录用户的用户名
    
    # 检查是否已经点赞
    existing_like = Like.query.filter_by(article_id=id, user=user).first()
    
    if existing_like:
        # 已经点赞，取消点赞
        article.likes -= 1
        db.session.delete(existing_like)
        db.session.commit()
        flash('取消点赞成功！', 'success')
    else:
        # 未点赞，添加点赞
        article.likes += 1
        new_like = Like(
            article_id=id,
            user=user
        )
        db.session.add(new_like)
        db.session.commit()
        flash('点赞成功！', 'success')
    
    return redirect(url_for('experience.article_detail', id=id))

# 搜索文章
@experience_bp.route('/search/')
def search_article():
    """搜索文章"""
    # 获取搜索关键词
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    if keyword:
        # 构建搜索查询
        query = Article.query.filter(
            (Article.title.like(f'%{keyword}%')) | 
            (Article.content.like(f'%{keyword}%')) |
            (Article.author.like(f'%{keyword}%'))
        )
        
        # 按创建时间倒序排列
        pagination = query.order_by(Article.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        articles = pagination.items
    else:
        articles = []
        pagination = None
    
    # 获取所有分类
    categories = ArticleCategory.query.all()
    
    return render_template('experience/search.html', articles=articles, categories=categories, pagination=pagination, keyword=keyword)

# 经验分享媒体文件访问
@experience_bp.route('/media/<filename>')
def experience_media(filename):
    """提供经验分享媒体文件访问"""
    return send_from_directory(os.path.join('static', 'uploads', 'experience'), filename)

