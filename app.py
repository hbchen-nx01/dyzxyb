from flask import Flask, render_template
from models import db, HonorBoard, WorkTask
from config import Config
import os

# 创建Flask应用实例
app = Flask(__name__, 
            static_url_path='/static',
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'),
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

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

# 注册路由蓝图
from routes.honor_board import honor_board_bp
from routes.employee import employee_bp
from routes.experience import experience_bp
from routes.work_task import work_task_bp
from routes.attendance import attendance_bp
from routes.fault_handling import fault_handling_bp
from routes.repair_recycle import repair_recycle_bp
from routes.training import training_bp
from routes.analytical_maintenance import analytical_maintenance_bp
from routes.document_management import document_management_bp
from routes.health import health_bp

app.register_blueprint(honor_board_bp, url_prefix='/honor-board')
app.register_blueprint(employee_bp, url_prefix='/employee')
app.register_blueprint(experience_bp, url_prefix='/experience')
app.register_blueprint(work_task_bp, url_prefix='/work-task')
app.register_blueprint(attendance_bp, url_prefix='/attendance')
app.register_blueprint(analytical_maintenance_bp, url_prefix='/analytical-maintenance')
app.register_blueprint(fault_handling_bp, url_prefix='/fault-handling')
app.register_blueprint(repair_recycle_bp, url_prefix='/repair-recycle')
app.register_blueprint(training_bp, url_prefix='/training')
app.register_blueprint(document_management_bp, url_prefix='/document-management')
app.register_blueprint(health_bp, url_prefix='/health')

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

if __name__ == '__main__':
    # 从环境变量获取端口，默认为5001
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
