# Netlify 404错误修复指南

## 问题分析
在Netlify上部署应用后出现404错误，可能的原因包括：

1. **函数初始化问题**：Flask应用在Netlify函数环境中没有正确初始化
2. **路由配置问题**：根路由没有正确处理
3. **数据库连接问题**：SQLite在无服务器环境中不可靠
4. **环境变量缺失**：必要的配置参数未设置
5. **文件路径问题**：函数无法找到应用文件

## 修复方案

### 1. 检查Netlify函数配置

#### 1.1 验证server.py文件
已更新`functions/server.py`文件，确保：
- 正确导入Flask应用
- 在应用上下文中初始化数据库
- 创建所有必要的表
- 设置上传目录

#### 1.2 测试函数是否工作
创建了`functions/test.py`测试函数，用于验证Netlify函数环境是否正常工作。

### 2. 配置外部数据库

由于Netlify的无服务器环境中文件系统是临时的，SQLite数据库会导致数据丢失。推荐使用外部数据库：

#### 2.1 推荐的数据库服务
- **Supabase**：免费的PostgreSQL服务，易于设置
- **Neon**：无服务器PostgreSQL
- **PlanetScale**：MySQL兼容的数据库

#### 2.2 获取数据库连接URL
在Netlify控制台中设置`DATABASE_URL`环境变量，格式为：
```
postgresql://username:password@host:port/database_name?sslmode=require
```

### 3. 配置环境变量

在Netlify控制台中添加以下环境变量：

| 环境变量名 | 描述 | 示例值 |
|------------|------|--------|
| SECRET_KEY | Flask应用密钥 | `your-secret-key-123` |
| DATABASE_URL | 外部数据库URL | `postgresql://user:pass@db.host:5432/dbname?sslmode=require` |
| FLASK_ENV | 运行环境 | `production` |

### 4. 重新部署应用

1. 保存所有更改并推送到GitHub仓库
2. Netlify会自动触发新的部署
3. 检查部署日志，确保没有错误

### 5. 验证部署

#### 5.1 检查函数日志
在Netlify控制台的"Functions"标签页查看server函数的日志，确认没有错误。

#### 5.2 测试路由
- 访问根URL：`https://your-site.netlify.app/`
- 测试其他路由：`https://your-site.netlify.app/analytical-maintenance/`

#### 5.3 测试测试函数
访问：`https://your-site.netlify.app/.netlify/functions/test`，应该看到JSON响应。

## 高级修复方案

### 1. 检查构建配置

确保`netlify.toml`文件中的配置正确：

```toml
[build]
  command = "pip install -r requirements.txt"
  functions = "functions"
  publish = "static"

[build.environment]
  PYTHON_VERSION = "3.10"

[functions]
  included_files = ["static/**/*", "templates/**/*", "instance/**/*"]

[[redirects]]
  from = "/*"
  to = "/.netlify/functions/server"
  status = 200
```

### 2. 检查依赖版本

确保`requirements.txt`中的依赖版本兼容：

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.1.1
WTForms==3.1.1
python-dotenv==1.0.0
numpy>=1.25.0
pandas==2.3.3
openpyxl==3.1.2
gunicorn==20.1.0
serverless-wsgi==3.1.0
Werkzeug>=3.0.0
```

### 3. 检查应用初始化

确保Flask应用在`app.py`中正确初始化：

```python
# 创建Flask应用实例
app = Flask(__name__)

# 加载配置
app.config.from_object(Config)

# 初始化数据库
with app.app_context():
    db.init_app(app)
    # 创建所有表
    db.create_all()
    
    # 确保上传目录存在
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
```

### 4. 检查根路由

确保根路由存在：

```python
@app.route('/')
def index():
    """首页路由"""
    # 获取任务状态统计
    status_counts = {
        'pending': WorkTask.query.filter_by(status='pending').count(),
        'in_progress': WorkTask.query.filter_by(status='in_progress').count(),
        'completed': WorkTask.query.filter_by(status='completed').count()
    }
    
    # 获取最近的工作任务（最多5个）
    recent_tasks = WorkTask.query.order_by(WorkTask.created_at.desc()).limit(5).all()
    
    return render_template('index.html', status_counts=status_counts, recent_tasks=recent_tasks)
```

## 常见问题解答

### Q: 为什么SQLite在Netlify上不可靠？
A: Netlify的无服务器环境中，文件系统是临时的。每次函数执行时，文件系统都会重置，导致SQLite数据库丢失。

### Q: 如何查看Netlify函数日志？
A: 在Netlify控制台中，进入项目的"Functions"标签页，点击"View logs"按钮。

### Q: 为什么需要配置环境变量？
A: 环境变量用于存储敏感信息和配置参数，确保应用在不同环境中正常工作。

### Q: 如何测试Netlify函数？
A: 可以通过Netlify CLI在本地测试函数，或者使用我们提供的`test.py`函数进行在线测试。

## 下一步

1. 按照本指南配置外部数据库
2. 在Netlify控制台中添加必要的环境变量
3. 重新部署应用
4. 验证部署是否成功

如果问题仍然存在，请检查Netlify部署日志，查找具体的错误信息，并联系Netlify支持团队获取帮助。