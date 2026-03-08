#!/usr/bin/env python3
"""
文件上传工具模块
支持本地存储和外部存储服务（如AWS S3、Cloudinary）
"""

import os
import uuid
from werkzeug.utils import secure_filename
from app import app


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def upload_file(file):
    """上传文件到配置的存储服务
    
    Args:
        file: Flask上传的文件对象
        
    Returns:
        tuple: (文件路径, 错误信息)
    """
    if not file or file.filename == '':
        return None, '未选择文件'
    
    if not allowed_file(file.filename):
        return None, '不支持的文件类型'
    
    # 生成安全的文件名
    filename = secure_filename(file.filename)
    # 添加唯一标识前缀，避免文件名冲突
    unique_filename = f"{uuid.uuid4()}_{filename}"
    
    storage_type = app.config.get('CLOUD_STORAGE_TYPE', 'local')
    
    if storage_type == 'aws_s3':
        return upload_to_s3(file, unique_filename)
    elif storage_type == 'cloudinary':
        return upload_to_cloudinary(file, unique_filename)
    else:
        return upload_to_local(file, unique_filename)


def upload_to_local(file, filename):
    """上传文件到本地存储"""
    try:
        # 确保上传目录存在
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        # 保存文件
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 返回相对路径（用于存储到数据库）
        return os.path.join('uploads', filename), None
    except Exception as e:
        return None, f'文件上传失败: {str(e)}'


def upload_to_s3(file, filename):
    """上传文件到AWS S3
    需要安装boto3: pip install boto3
    """
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError
        
        # 获取AWS配置
        aws_access_key = app.config.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = app.config.get('AWS_SECRET_ACCESS_KEY')
        aws_bucket = app.config.get('AWS_S3_BUCKET')
        aws_region = app.config.get('AWS_S3_REGION', 'us-east-1')
        
        if not all([aws_access_key, aws_secret_key, aws_bucket]):
            return None, 'AWS S3配置不完整'
        
        # 创建S3客户端
        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
        # 上传文件
        s3.upload_fileobj(
            file,
            aws_bucket,
            filename,
            ExtraArgs={
                'ContentType': file.content_type
            }
        )
        
        # 生成文件URL
        file_url = f"https://{aws_bucket}.s3.{aws_region}.amazonaws.com/{filename}"
        return file_url, None
        
    except ImportError:
        return None, '缺少boto3库，请安装: pip install boto3'
    except NoCredentialsError:
        return None, 'AWS凭证错误'
    except Exception as e:
        return None, f'上传到S3失败: {str(e)}'


def upload_to_cloudinary(file, filename):
    """上传文件到Cloudinary
    需要安装cloudinary: pip install cloudinary
    """
    try:
        import cloudinary
        import cloudinary.uploader
        
        # 获取Cloudinary配置
        cloud_name = app.config.get('CLOUDINARY_CLOUD_NAME')
        api_key = app.config.get('CLOUDINARY_API_KEY')
        api_secret = app.config.get('CLOUDINARY_API_SECRET')
        
        if not all([cloud_name, api_key, api_secret]):
            return None, 'Cloudinary配置不完整'
        
        # 配置Cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        
        # 上传文件
        result = cloudinary.uploader.upload(
            file,
            public_id=os.path.splitext(filename)[0],
            folder='app_uploads'
        )
        
        # 返回文件URL
        return result['secure_url'], None
        
    except ImportError:
        return None, '缺少cloudinary库，请安装: pip install cloudinary'
    except Exception as e:
        return None, f'上传到Cloudinary失败: {str(e)}'


def get_file_url(file_path):
    """根据文件路径获取完整URL
    
    Args:
        file_path: 存储在数据库中的文件路径
        
    Returns:
        str: 文件的完整URL
    """
    if not file_path:
        return ''
    
    # 如果是完整URL，直接返回
    if file_path.startswith(('http://', 'https://')):
        return file_path
    
    storage_type = app.config.get('CLOUD_STORAGE_TYPE', 'local')
    
    if storage_type == 'local':
        # 本地存储返回相对路径
        return file_path
    else:
        # 外部存储服务应该已经存储了完整URL
        return file_path