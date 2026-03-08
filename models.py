from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 创建数据库实例
db = SQLAlchemy()

class HonorBoard(db.Model):
    """光荣榜数据模型"""
    __tablename__ = 'honor_board'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_name = db.Column(db.String(100), nullable=False, comment='人员姓名')
    award_type = db.Column(db.String(100), nullable=False, comment='奖励类型')
    award_content = db.Column(db.Text, nullable=False, comment='奖励内容')
    award_date = db.Column(db.Date, nullable=False, comment='获得时间')
    image_path = db.Column(db.String(255), nullable=True, comment='图片路径')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<HonorBoard {self.id}: {self.employee_name} - {self.award_type}>'

class Employee(db.Model):
    """员工基本信息模型"""
    __tablename__ = 'employee'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False, comment='员工编号')
    name = db.Column(db.String(100), nullable=False, comment='姓名')
    gender = db.Column(db.String(10), nullable=False, comment='性别')
    birthday = db.Column(db.Date, nullable=False, comment='出生年月日')
    position = db.Column(db.String(100), nullable=False, comment='岗位分类')
    contact = db.Column(db.String(100), nullable=False, comment='联系方式')
    education = db.Column(db.String(100), nullable=False, comment='学历')
    school = db.Column(db.String(200), nullable=False, comment='院校')
    sort_order = db.Column(db.Integer, default=0, nullable=False, comment='排序顺序')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    skill_levels = db.relationship('SkillLevel', backref='employee', cascade='all, delete-orphan')
    training_experiences = db.relationship('TrainingExperience', backref='employee', cascade='all, delete-orphan')
    qualification_certificates = db.relationship('QualificationCertificate', backref='employee', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Employee {self.id}: {self.employee_id} - {self.name}>'

class SkillLevel(db.Model):
    """技能等级模型"""
    __tablename__ = 'skill_level'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, comment='员工ID')
    skill_name = db.Column(db.String(100), nullable=False, comment='技能名称')
    level = db.Column(db.String(50), nullable=False, comment='技能等级')
    obtained_date = db.Column(db.Date, nullable=False, comment='获得日期')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<SkillLevel {self.id}: {self.skill_name} - {self.level}>'

class TrainingExperience(db.Model):
    """培训经历模型"""
    __tablename__ = 'training_experience'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, comment='员工ID')
    training_name = db.Column(db.String(200), nullable=False, comment='培训名称')
    training_organization = db.Column(db.String(200), nullable=False, comment='培训组织')
    start_date = db.Column(db.Date, nullable=False, comment='开始日期')
    end_date = db.Column(db.Date, nullable=False, comment='结束日期')
    training_content = db.Column(db.Text, nullable=False, comment='培训内容')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<TrainingExperience {self.id}: {self.training_name}>'

class QualificationCertificate(db.Model):
    """资质证书模型"""
    __tablename__ = 'qualification_certificate'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, comment='员工ID')
    certificate_name = db.Column(db.String(200), nullable=False, comment='证书名称')
    certificate_number = db.Column(db.String(100), nullable=False, comment='证书编号')
    issued_by = db.Column(db.String(200), nullable=False, comment='发证机构')
    issued_date = db.Column(db.Date, nullable=False, comment='发证日期')
    valid_until = db.Column(db.Date, nullable=True, comment='有效期至')
    file_path = db.Column(db.String(255), nullable=True, comment='证书文件路径')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<QualificationCertificate {self.id}: {self.certificate_name}>'

class ArticleCategory(db.Model):
    """文章分类模型"""
    __tablename__ = 'article_category'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='分类名称')
    description = db.Column(db.Text, nullable=True, comment='分类描述')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    articles = db.relationship('Article', backref='category', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ArticleCategory {self.id}: {self.name}>'

class Article(db.Model):
    """文章模型"""
    __tablename__ = 'article'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(20), default='article', comment='类型：article（长文章）/share（一句话分享）')
    title = db.Column(db.String(200), nullable=True, comment='文章标题，短分享可以为空')
    content = db.Column(db.Text, nullable=False, comment='文章内容')
    category_id = db.Column(db.Integer, db.ForeignKey('article_category.id'), nullable=False, comment='分类ID')
    author = db.Column(db.String(100), nullable=False, comment='作者')
    views = db.Column(db.Integer, default=0, comment='浏览次数')
    likes = db.Column(db.Integer, default=0, comment='点赞数')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    media = db.relationship('ArticleMedia', backref='article', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='article', cascade='all, delete-orphan')
    likes_list = db.relationship('Like', backref='article', cascade='all, delete-orphan')
    
    @property
    def is_short(self):
        """是否为短分享"""
        return self.type == 'share'
    
    def __repr__(self):
        if self.title:
            return f'<Article {self.id}: {self.title} ({self.type})>'
        else:
            return f'<Article {self.id}: {self.content[:20]}... ({self.type})>'

class ArticleMedia(db.Model):
    """文章多媒体模型"""
    __tablename__ = 'article_media'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False, comment='文章ID')
    file_path = db.Column(db.String(255), nullable=False, comment='文件路径')
    file_type = db.Column(db.String(20), nullable=False, comment='文件类型（image/video）')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    def __repr__(self):
        return f'<ArticleMedia {self.id}: {self.file_path}>'

class Comment(db.Model):
    """评论模型"""
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False, comment='文章ID')
    content = db.Column(db.Text, nullable=False, comment='评论内容')
    author = db.Column(db.String(100), nullable=False, comment='评论作者')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    def __repr__(self):
        return f'<Comment {self.id}>'

class Like(db.Model):
    """点赞模型"""
    __tablename__ = 'like'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False, comment='文章ID')
    user = db.Column(db.String(100), nullable=False, comment='点赞用户')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    def __repr__(self):
        return f'<Like {self.id}>'

class WorkTask(db.Model):
    """工作任务模型"""
    __tablename__ = 'work_task'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False, comment='任务标题')
    description = db.Column(db.Text, nullable=True, comment='任务描述')
    assigned_to = db.Column(db.String(100), nullable=False, comment='分配人员')
    assigned_type = db.Column(db.String(20), nullable=False, default='employee', comment='分配类型：employee（员工）/contractor（承包商）')
    status = db.Column(db.String(20), nullable=False, default='pending', comment='任务状态：pending（未开始）/in_progress（进行中）/completed（已完成）')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    completed_at = db.Column(db.DateTime, nullable=True, comment='完成时间')
    
    # 关系定义
    reports = db.relationship('WorkReport', backref='task', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<WorkTask {self.id}: {self.title}>'

class WorkReport(db.Model):
    """工作日报模型"""
    __tablename__ = 'work_report'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('work_task.id'), nullable=False, comment='任务ID')
    report_date = db.Column(db.Date, nullable=False, default=datetime.utcnow, comment='报告日期')
    content = db.Column(db.Text, nullable=False, comment='日报内容')
    author = db.Column(db.String(100), nullable=False, comment='报告作者')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<WorkReport {self.id}: {self.report_date}>'

class EquipmentCategory(db.Model):
    """设备分类模型"""
    __tablename__ = 'equipment_category'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='分类名称')
    parent_id = db.Column(db.Integer, db.ForeignKey('equipment_category.id'), nullable=True, comment='父分类ID')
    description = db.Column(db.Text, nullable=True, comment='分类描述')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    parent = db.relationship('EquipmentCategory', remote_side=[id], backref=db.backref('children', lazy=True))
    equipments = db.relationship('Equipment', backref='category', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<EquipmentCategory {self.id}: {self.name}>'


class Equipment(db.Model):
    """设备模型"""
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equipment_number = db.Column(db.String(100), unique=True, nullable=False, comment='设备位号')
    name = db.Column(db.String(200), nullable=False, comment='设备名称')
    model = db.Column(db.String(100), nullable=True, comment='设备型号')
    specification = db.Column(db.String(200), nullable=True, comment='规格')
    serial_number = db.Column(db.String(100), nullable=True, comment='设备序列号')
    category_id = db.Column(db.Integer, db.ForeignKey('equipment_category.id'), nullable=True, comment='设备分类ID')
    location = db.Column(db.String(200), nullable=True, comment='安装位置')
    department = db.Column(db.String(100), nullable=True, comment='使用部门')
    responsible_person = db.Column(db.String(100), nullable=True, comment='责任人')
    phone = db.Column(db.String(20), nullable=True, comment='联系方式')
    description = db.Column(db.Text, nullable=True, comment='设备描述')
    
    # 新增字段
    unit_number = db.Column(db.String(50), nullable=True, comment='单元号')
    equipment_type = db.Column(db.String(50), nullable=True, comment='设备类型')
    specs_json = db.Column(db.JSON, nullable=True, comment='设备特有属性（JSON格式）')
    
    # 采购信息
    purchase_date = db.Column(db.Date, nullable=True, comment='采购日期')
    purchase_price = db.Column(db.Float, nullable=True, comment='采购价格（元）')
    manufacturer = db.Column(db.String(200), nullable=True, comment='制造商')
    supplier = db.Column(db.String(200), nullable=True, comment='供应商')
    warranty_period = db.Column(db.Integer, nullable=True, comment='保修期（月）')
    
    # 设备状态
    status = db.Column(db.String(20), nullable=False, default='in_use', comment='设备状态：in_use（在用）、idle（闲置）、scrapped（报废）、repairing（维修中）')
    
    # 维护信息
    last_maintenance_date = db.Column(db.Date, nullable=True, comment='本次维护日期')
    next_maintenance_date = db.Column(db.Date, nullable=True, comment='下次维护日期')
    maintenance_interval = db.Column(db.Integer, nullable=True, comment='维护时间间隔（天）')
    
    # 报废信息
    scrap_date = db.Column(db.Date, nullable=True, comment='报废日期')
    scrap_reason = db.Column(db.Text, nullable=True, comment='报废原因')
    scrap_value = db.Column(db.Float, nullable=True, comment='报废价值（元）')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    maintenance_plans = db.relationship('MaintenancePlan', backref='equipment', cascade='all, delete-orphan')
    maintenance_records = db.relationship('MaintenanceRecord', backref='equipment', cascade='all, delete-orphan')
    fault_records = db.relationship('FaultRecord', backref='equipment', cascade='all, delete-orphan')
    repair_records = db.relationship('RepairRecycle', backref='equipment', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Equipment {self.id}: {self.name}>'

class MaintenancePlan(db.Model):
    """维护计划模型"""
    __tablename__ = 'maintenance_plan'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False, comment='设备ID')
    plan_name = db.Column(db.String(200), nullable=False, comment='计划名称')
    description = db.Column(db.Text, nullable=True, comment='计划描述')
    maintenance_type = db.Column(db.String(100), nullable=False, comment='维护类型')
    frequency = db.Column(db.String(20), nullable=False, default='monthly', comment='维护频率：daily/weekly/monthly/quarterly/yearly')
    next_maintenance_date = db.Column(db.Date, nullable=False, default=datetime.utcnow, comment='下次维护日期')
    created_by = db.Column(db.String(100), nullable=False, comment='创建人')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    records = db.relationship('MaintenanceRecord', backref='plan', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<MaintenancePlan {self.id}: {self.plan_name}>'

class MaintenanceRecord(db.Model):
    """维护记录模型"""
    __tablename__ = 'maintenance_record'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('maintenance_plan.id'), nullable=False, comment='维护计划ID')
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False, comment='设备ID')
    maintenance_date = db.Column(db.Date, nullable=False, default=datetime.utcnow, comment='维护日期')
    executor = db.Column(db.String(100), nullable=False, comment='执行人')
    content = db.Column(db.Text, nullable=False, comment='维护内容')
    result = db.Column(db.String(20), nullable=False, default='success', comment='维护结果：success/failure')
    notes = db.Column(db.Text, nullable=True, comment='备注')
    
    # 新增：维护消耗品记录
    spare_parts_used = db.Column(db.Text, nullable=True, comment='使用的备件')
    maintenance_cost = db.Column(db.Float, nullable=True, comment='维护成本（元）')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<MaintenanceRecord {self.id}: {self.maintenance_date}>'

class FaultRecord(db.Model):
    """设备故障记录模型"""
    __tablename__ = 'fault_record'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False, comment='设备ID')
    fault_phenomenon = db.Column(db.Text, nullable=False, comment='故障现象')
    occurrence_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='故障发生时间')
    reporter = db.Column(db.String(100), nullable=False, comment='报告人')
    fault_type = db.Column(db.String(100), nullable=True, comment='故障类型')
    fault_image = db.Column(db.String(255), nullable=True, comment='故障图片路径')
    status = db.Column(db.String(20), nullable=False, default='reported', comment='故障状态：reported（已报告）/in_progress（处理中）/resolved（已解决）/closed（已关闭）')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 新增：故障影响和紧急程度
    impact_level = db.Column(db.String(20), nullable=True, comment='影响程度：critical（严重）/major（主要）/minor（次要）')
    urgency_level = db.Column(db.String(20), nullable=True, comment='紧急程度：urgent（紧急）/high（高）/medium（中）/low（低）')
    
    # 关系定义
    solutions = db.relationship('FaultSolution', backref='fault_record', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<FaultRecord {self.id}: {self.equipment_id} - {self.fault_phenomenon[:20]}>'

class FaultSolution(db.Model):
    """故障处理解决方案模型"""
    __tablename__ = 'fault_solution'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fault_id = db.Column(db.Integer, db.ForeignKey('fault_record.id'), nullable=False, comment='故障记录ID')
    handler = db.Column(db.String(100), nullable=False, comment='处理人')
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='开始处理时间')
    end_time = db.Column(db.DateTime, nullable=True, comment='结束处理时间')
    process_description = db.Column(db.Text, nullable=True, comment='故障处理过程')
    solution = db.Column(db.Text, nullable=False, comment='解决方案')
    verification_result = db.Column(db.String(20), nullable=True, comment='验证结果：passed（通过）/failed（失败）')
    notes = db.Column(db.Text, nullable=True, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 新增：故障处理相关字段
    spare_parts_used = db.Column(db.Text, nullable=True, comment='使用的备件')
    repair_cost = db.Column(db.Float, nullable=True, comment='维修成本（元）')
    
    @property
    def handling_duration(self):
        """计算故障处理时长"""
        if self.end_time:
            duration = self.end_time - self.start_time
            return duration.total_seconds() / 3600  # 返回小时数
        return None
    
    def __repr__(self):
        return f'<FaultSolution {self.id}: Fault {self.fault_id} - {self.handler}>'

class RepairRecycle(db.Model):
    """修旧利废台账模型"""
    __tablename__ = 'repair_recycle'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=True, comment='设备ID')
    equipment_name = db.Column(db.String(200), nullable=False, comment='设备名称')
    project_name = db.Column(db.String(200), nullable=False, comment='项目名称')
    repair_date = db.Column(db.Date, nullable=False, default=datetime.utcnow, comment='修复日期')
    repair_person = db.Column(db.String(100), nullable=False, comment='修复人员')
    before_status = db.Column(db.Text, nullable=False, comment='修复前状态')
    after_status = db.Column(db.Text, nullable=False, comment='修复后状态')
    before_value = db.Column(db.Float, nullable=False, comment='修复前价值（元）')
    after_value = db.Column(db.Float, nullable=False, comment='修复后价值（元）')
    before_image_path = db.Column(db.String(255), nullable=True, comment='修复前图片路径')
    after_image_path = db.Column(db.String(255), nullable=True, comment='修复后图片路径')
    description = db.Column(db.Text, nullable=True, comment='项目描述')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    @property
    def benefit(self):
        """计算效益（修复后价值 - 修复前价值）"""
        return self.after_value - self.before_value
    
    def __repr__(self):
        return f'<RepairRecycle {self.id}: {self.project_name}>'

class TrainingPlan(db.Model):
    """培训计划模型"""
    __tablename__ = 'training_plan'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False, comment='培训主题')
    description = db.Column(db.Text, nullable=True, comment='培训描述')
    trainer = db.Column(db.String(100), nullable=False, comment='讲师')
    start_date = db.Column(db.DateTime, nullable=False, comment='开始时间')
    end_date = db.Column(db.DateTime, nullable=False, comment='结束时间')
    location = db.Column(db.String(200), nullable=False, comment='培训地点')
    status = db.Column(db.String(20), nullable=False, default='planned', comment='状态：planned（计划中）/in_progress（进行中）/completed（已完成）/cancelled（已取消）')
    created_by = db.Column(db.String(100), nullable=False, comment='创建人')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    participants = db.relationship('TrainingParticipant', backref='training_plan', cascade='all, delete-orphan')
    materials = db.relationship('TrainingMaterial', backref='training_plan', cascade='all, delete-orphan')
    evaluations = db.relationship('TrainingEvaluation', backref='training_plan', cascade='all, delete-orphan')
    certificates = db.relationship('TrainingCertificate', backref='training_plan', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TrainingPlan {self.id}: {self.title}>'

class TrainingParticipant(db.Model):
    """培训参与人员模型"""
    __tablename__ = 'training_participant'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    training_id = db.Column(db.Integer, db.ForeignKey('training_plan.id'), nullable=False, comment='培训计划ID')
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, comment='员工ID')
    attendance = db.Column(db.Boolean, nullable=False, default=True, comment='是否出勤')
    score = db.Column(db.Float, nullable=True, comment='考核分数')
    assessment = db.Column(db.String(20), nullable=True, comment='考核结果：excellent（优秀）/good（良好）/pass（及格）/fail（不及格）')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    employee = db.relationship('Employee', backref=db.backref('training_participants', lazy=True))
    
    def __repr__(self):
        return f'<TrainingParticipant {self.id}: Employee {self.employee_id} in Training {self.training_id}>'

class TrainingMaterial(db.Model):
    """培训资料模型"""
    __tablename__ = 'training_material'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    training_id = db.Column(db.Integer, db.ForeignKey('training_plan.id'), nullable=False, comment='培训计划ID')
    title = db.Column(db.String(200), nullable=False, comment='资料名称')
    file_path = db.Column(db.String(255), nullable=False, comment='文件路径')
    file_type = db.Column(db.String(50), nullable=False, comment='文件类型')
    description = db.Column(db.Text, nullable=True, comment='资料描述')
    uploaded_by = db.Column(db.String(100), nullable=False, comment='上传人')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    def __repr__(self):
        return f'<TrainingMaterial {self.id}: {self.title}>'

class TrainingEvaluation(db.Model):
    """培训效果评估模型"""
    __tablename__ = 'training_evaluation'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    training_id = db.Column(db.Integer, db.ForeignKey('training_plan.id'), nullable=False, comment='培训计划ID')
    evaluator = db.Column(db.String(100), nullable=False, comment='评估人')
    content_relevance = db.Column(db.Integer, nullable=False, comment='内容相关性评分（1-5）')
    trainer_effectiveness = db.Column(db.Integer, nullable=False, comment='讲师效果评分（1-5）')
    overall_satisfaction = db.Column(db.Integer, nullable=False, comment='总体满意度评分（1-5）')
    comments = db.Column(db.Text, nullable=True, comment='评估意见')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    def __repr__(self):
        return f'<TrainingEvaluation {self.id}: Training {self.training_id}>'

class TrainingCertificate(db.Model):
    """培训证书模型"""
    __tablename__ = 'training_certificate'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    training_id = db.Column(db.Integer, db.ForeignKey('training_plan.id'), nullable=False, comment='培训计划ID')
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, comment='员工ID')
    certificate_number = db.Column(db.String(100), unique=True, nullable=False, comment='证书编号')
    issue_date = db.Column(db.Date, nullable=False, default=datetime.utcnow, comment='颁发日期')
    valid_until = db.Column(db.Date, nullable=True, comment='有效期至')
    certificate_path = db.Column(db.String(255), nullable=True, comment='证书文件路径')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    # 关系定义
    employee = db.relationship('Employee', backref=db.backref('training_certificates', lazy=True))
    
    def __repr__(self):
        return f'<TrainingCertificate {self.id}: Employee {self.employee_id} - Training {self.training_id}>'


class AttendanceRecord(db.Model):
    """考勤记录模型"""
    __tablename__ = 'attendance_record'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, comment='员工ID')
    attendance_date = db.Column(db.Date, nullable=False, comment='考勤日期')
    status = db.Column(db.String(10), nullable=False, default='1', comment='考勤状态：1（正常），换（换班），值（值班），年（年假），病（病假），事（事假），产（产假），婚（婚假），丧（丧假），抚（抚恤假），探（探亲假），育（育儿假），伤（工伤假），旷（旷工），护（护理假）')
    check_in_time = db.Column(db.Time, nullable=True, comment='上班打卡时间')
    check_out_time = db.Column(db.Time, nullable=True, comment='下班打卡时间')
    notes = db.Column(db.Text, nullable=True, comment='备注')
    created_by = db.Column(db.String(100), nullable=True, comment='创建人')
    updated_by = db.Column(db.String(100), nullable=True, comment='更新人')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    employee = db.relationship('Employee', backref=db.backref('attendance_records', lazy=True))
    
    def __repr__(self):
        return f'<AttendanceRecord {self.id}: Employee {self.employee_id} on {self.attendance_date}>'


class LeaveApplication(db.Model):
    """请假申请模型"""
    __tablename__ = 'leave_application'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, comment='员工ID')
    leave_type = db.Column(db.String(10), nullable=False, comment='请假类型：年（年假），病（病假），事（事假），产（产假），婚（婚假），丧（丧假），抚（抚恤假），探（探亲假），育（育儿假），伤（工伤假），护（护理假）')
    start_date = db.Column(db.Date, nullable=False, comment='开始日期')
    end_date = db.Column(db.Date, nullable=False, comment='结束日期')
    start_time = db.Column(db.Time, nullable=True, comment='开始时间（半天假使用）')
    end_time = db.Column(db.Time, nullable=True, comment='结束时间（半天假使用）')
    duration = db.Column(db.Float, nullable=False, comment='请假时长（天）')
    reason = db.Column(db.Text, nullable=False, comment='请假原因')
    status = db.Column(db.String(20), nullable=False, default='pending', comment='状态：pending（待审批），approved（已批准），rejected（已拒绝），cancelled（已取消）')
    approver = db.Column(db.String(100), nullable=True, comment='审批人')
    approval_time = db.Column(db.DateTime, nullable=True, comment='审批时间')
    approval_comments = db.Column(db.Text, nullable=True, comment='审批意见')
    # 图片上传字段
    attachment = db.Column(db.String(255), nullable=True, comment='请假证明图片')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    employee = db.relationship('Employee', backref=db.backref('leave_applications', lazy=True))
    
    def __repr__(self):
        return f'<LeaveApplication {self.id}: Employee {self.employee_id} - {self.leave_type}>'


class OvertimeApplication(db.Model):
    """加班申请模型"""
    __tablename__ = 'overtime_application'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, comment='员工ID')
    overtime_date = db.Column(db.Date, nullable=False, comment='加班日期')
    start_time = db.Column(db.Time, nullable=False, comment='开始时间')
    end_time = db.Column(db.Time, nullable=False, comment='结束时间')
    duration = db.Column(db.Float, nullable=False, comment='加班时长（小时）')
    reason = db.Column(db.Text, nullable=False, comment='加班原因')
    status = db.Column(db.String(20), nullable=False, default='pending', comment='状态：pending（待审批），approved（已批准），rejected（已拒绝），cancelled（已取消）')
    approver = db.Column(db.String(100), nullable=True, comment='审批人')
    approval_time = db.Column(db.DateTime, nullable=True, comment='审批时间')
    approval_comments = db.Column(db.Text, nullable=True, comment='审批意见')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    employee = db.relationship('Employee', backref=db.backref('overtime_applications', lazy=True))
    
    def __repr__(self):
        return f'<OvertimeApplication {self.id}: Employee {self.employee_id} on {self.overtime_date}>'


class Holiday(db.Model):
    """节假日模型"""
    __tablename__ = 'holiday'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    holiday_date = db.Column(db.Date, unique=True, nullable=False, comment='节假日日期')
    name = db.Column(db.String(100), nullable=False, comment='节假日名称')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    # 关系定义
    duties = db.relationship('HolidayDuty', backref='holiday', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Holiday {self.id}: {self.name} on {self.holiday_date}>'


class HolidayDuty(db.Model):
    """节假日值班安排模型"""
    __tablename__ = 'holiday_duty'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    holiday_id = db.Column(db.Integer, db.ForeignKey('holiday.id'), nullable=False, comment='节假日ID')
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, comment='员工ID')
    duty_time = db.Column(db.String(20), nullable=False, comment='值班时段：上午/下午/全天')
    contact_info = db.Column(db.String(200), nullable=False, comment='联系方式')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    employee = db.relationship('Employee', backref=db.backref('holiday_duties', lazy=True))
    
    def __repr__(self):
        return f'<HolidayDuty {self.id}: Employee {self.employee_id} on Holiday {self.holiday_id}>'

class DocumentCategory(db.Model):
    """文档分类模型"""
    __tablename__ = 'document_category'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='分类名称')
    parent_id = db.Column(db.Integer, db.ForeignKey('document_category.id'), nullable=True, comment='父分类ID')
    description = db.Column(db.Text, nullable=True, comment='分类描述')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    parent = db.relationship('DocumentCategory', remote_side=[id], backref=db.backref('children', lazy=True))
    documents = db.relationship('Document', backref='category', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<DocumentCategory {self.id}: {self.name}>'

class Document(db.Model):
    """文档模型"""
    __tablename__ = 'document'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False, comment='文档标题')
    category_id = db.Column(db.Integer, db.ForeignKey('document_category.id'), nullable=False, comment='分类ID')
    file_path = db.Column(db.String(255), nullable=False, comment='文件路径')
    file_name = db.Column(db.String(200), nullable=False, comment='文件名')
    file_size = db.Column(db.Integer, nullable=False, comment='文件大小（字节）')
    uploader = db.Column(db.String(100), nullable=False, comment='上传人')
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, comment='上传日期')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<Document {self.id}: {self.title}>'


class EmployeeHealthRecord(db.Model):
    """员工健康记录模型"""
    __tablename__ = 'employee_health_record'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, comment='员工ID')
    record_date = db.Column(db.Date, nullable=False, comment='记录日期')
    mental_state = db.Column(db.Integer, nullable=False, default=5, comment='情绪状态（0-10分）')
    physical_health = db.Column(db.Integer, nullable=False, default=5, comment='身体健康（0-10分）')
    work_suitability = db.Column(db.Boolean, nullable=False, default=True, comment='工作适配性：True（适合工作）/False（不适合工作）')
    mood_diary = db.Column(db.Text, nullable=True, comment='心情日记')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    employee = db.relationship('Employee', backref=db.backref('health_records', lazy=True))
    
    def __repr__(self):
        return f'<EmployeeHealthRecord {self.id}: Employee {self.employee_id} on {self.record_date}>'


class TeamHealthStats(db.Model):
    """班组健康统计模型"""
    __tablename__ = 'team_health_stats'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stat_date = db.Column(db.Date, nullable=False, unique=True, comment='统计日期')
    total_employees = db.Column(db.Integer, nullable=False, default=0, comment='总人数')
    available = db.Column(db.Integer, nullable=False, default=0, comment='适合工作人数')
    unavailable = db.Column(db.Integer, nullable=False, default=0, comment='不适合工作人数')
    avg_mental_state = db.Column(db.Float, nullable=True, comment='平均情绪状态')
    avg_physical_health = db.Column(db.Float, nullable=True, comment='平均身体健康')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<TeamHealthStats {self.id}: {self.stat_date}>'
