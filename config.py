import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')  # 用于CSRF保护和会话管理
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # 数据库配置 - 优先从环境变量读取DATABASE_URL
    # 支持PostgreSQL, MySQL, SQLite等数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "app.db")}')
    # 如果是PostgreSQL，确保添加sslmode参数
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上传配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'static', 'uploads'))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'zip', 'rar'}  # 允许上传的文件格式
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 最大上传大小16MB
    
    # 外部存储服务配置（可选，用于生产环境）
    CLOUD_STORAGE_TYPE = os.environ.get('CLOUD_STORAGE_TYPE', 'local')  # local, aws_s3, cloudinary
    
    # AWS S3配置
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
    AWS_S3_REGION = os.environ.get('AWS_S3_REGION')
    
    # Cloudinary配置
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    
    # 图片文件夹路径（用于打开文件夹功能）
    UPLOAD_FOLDER_ABSOLUTE = UPLOAD_FOLDER
