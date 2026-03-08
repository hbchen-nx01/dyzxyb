# 班组管理系统项目文档

## 1. 项目概述

### 1.1 项目简介
班组管理系统是一个基于Flask框架开发的Web应用，用于管理企业班组的日常工作和人员信息。系统提供了多个功能模块，包括员工管理、考勤管理、工作任务安排、设备维护等。

### 1.2 技术栈
- **后端**：Python 3.14+, Flask 3.0.0
- **数据库**：SQLite（本地开发）/ PostgreSQL（生产环境）
- **前端**：HTML5, CSS3, Bootstrap 5
- **其他依赖**：Flask-SQLAlchemy, Flask-WTF, pandas, openpyxl

## 2. 项目结构

```
├── app.py                 # 应用入口文件
├── wsgi.py                # WSGI服务器入口
├── config.py              # 应用配置
├── models.py              # 数据库模型
├── requirements.txt       # 项目依赖
├── vercel.json            # Vercel部署配置
├── Procfile               # 生产环境启动配置
├── .env.example           # 环境变量示例
├── routes/                # 路由蓝图
│   ├── __init__.py
│   ├── honor_board.py     # 光荣榜模块
│   ├── employee.py        # 员工信息管理
│   ├── experience.py      # 经验分享
│   ├── work_task.py       # 每日工作安排
│   ├── attendance.py      # 考勤管理
│   ├── fault_handling.py  # 设备故障处理
│   ├── repair_recycle.py  # 修旧利废台账
│   ├── training.py        # 班组培训计划
│   ├── analytical_maintenance.py  # 仪表维护
│   ├── document_management.py     # 文档管理
│   └── health.py          # 员工情绪与健康管理
├── templates/             # 模板文件
│   ├── base.html          # 基础模板
│   ├── index.html         # 首页
│   ├── honor_board/       # 光荣榜模板
│   ├── employee/          # 员工管理模板
│   ├── experience/        # 经验分享模板
│   ├── work_task/         # 工作任务模板
│   ├── attendance/        # 考勤管理模板
│   ├── fault_handling/    # 故障处理模板
│   ├── repair_recycle/    # 修旧利废模板
│   ├── training/          # 培训计划模板
│   ├── analytical_maintenance/  # 仪表维护模板
│   ├── document_management/     # 文档管理模板
│   └── health/            # 健康管理模板
├── static/                # 静态文件
│   ├── css/               # 样式文件
│   ├── js/                # JavaScript文件
│   └── uploads/           # 上传文件
├── utils/                 # 工具函数
│   └── file_upload.py     # 文件上传工具
└── instance/              # 实例文件（数据库等）
```

## 3. 功能模块

### 3.1 光荣榜
- 展示员工荣誉和表彰
- 添加、编辑、删除荣誉记录

### 3.2 员工信息管理
- 员工基本信息管理
- 员工技能等级管理
- 员工资格证书管理
- 员工培训经历管理
- Excel导入/导出功能

### 3.3 员工情绪与健康管理
- 员工情绪记录
- 健康状况跟踪
- 数据分析和统计

### 3.4 经验分享
- 经验文章发布
- 文章分类和搜索
- 评论和互动

### 3.5 每日工作安排
- 工作任务创建和分配
- 任务状态跟踪
- 任务进度报告
- 统计分析

### 3.6 考勤管理
- 日常考勤记录
- 请假申请和审批
- 加班申请和审批
- 考勤统计和报表
- 节假日和值班安排

### 3.7 仪表维护
- 设备台账管理
- 预防性维护计划
- 维护记录跟踪
- 故障分析和统计

### 3.8 设备故障处理
- 故障记录管理
- 故障解决方案
- 故障案例分析
- 统计报表

### 3.9 修旧利废台账
- 修旧利废记录
- 成本节约统计
- 详细信息管理

### 3.10 班组培训计划
- 培训计划制定
- 培训材料管理
- 培训参与人员管理
- 培训效果评估
- 证书管理

### 3.11 文档管理
- 文档上传和管理
- 文档分类
- 文档搜索和预览

## 4. 部署说明

### 4.1 本地开发环境

#### 4.1.1 安装依赖
```bash
pip install -r requirements.txt
```

#### 4.1.2 运行应用
```bash
python app.py
```

#### 4.1.3 访问地址
- http://127.0.0.1:5001

### 4.2 Vercel部署

#### 4.2.1 配置文件
- `vercel.json`：Vercel部署配置
- `requirements.txt`：项目依赖

#### 4.2.2 环境变量
需要在Vercel控制台设置以下环境变量：
- `SECRET_KEY`：用于Flask的CSRF保护和会话管理
- `DATABASE_URL`：数据库连接字符串（推荐使用Vercel Postgres）
- `UPLOAD_FOLDER`：文件上传目录
- `FLASK_ENV`：production

#### 4.2.3 部署步骤
1. 将代码推送到GitHub仓库
2. 在Vercel控制台导入GitHub仓库
3. 配置环境变量
4. 点击部署按钮
5. 等待部署完成

## 5. 数据库设计

### 5.1 主要表结构
- `honor_board`：光荣榜记录
- `employee`：员工信息
- `skill_level`：员工技能等级
- `qualification_certificate`：员工资格证书
- `training_experience`：员工培训经历
- `health_record`：健康记录
- `experience_article`：经验分享文章
- `work_task`：工作任务
- `attendance_record`：考勤记录
- `leave_application`：请假申请
- `overtime_application`：加班申请
- `equipment`：设备信息
- `maintenance_plan`：维护计划
- `maintenance_record`：维护记录
- `fault_record`：故障记录
- `fault_solution`：故障解决方案
- `repair_recycle`：修旧利废记录
- `training_plan`：培训计划
- `document`：文档记录

## 6. 系统功能使用说明

### 6.1 首页
- 展示系统概览
- 显示任务状态统计
- 展示最近工作任务

### 6.2 员工管理
- 点击"员工信息管理"进入员工列表
- 点击"添加"按钮添加新员工
- 点击"编辑"按钮修改员工信息
- 点击"详情"按钮查看员工详细信息
- 支持Excel导入员工数据

### 6.3 考勤管理
- 点击"考勤管理"进入考勤系统
- 选择日期进行日常考勤记录
- 提交请假和加班申请
- 审批请假和加班申请
- 查看考勤统计报表

### 6.4 工作任务
- 点击"每日工作安排"进入任务管理
- 点击"添加"按钮创建新任务
- 分配任务给员工
- 更新任务状态
- 提交任务报告

### 6.5 设备维护
- 点击"仪表维护"进入设备管理
- 添加和管理设备信息
- 创建维护计划
- 记录维护情况
- 分析设备故障

## 7. 系统配置

### 7.1 配置文件
- `config.py`：应用配置
- `.env`：环境变量（本地开发）

### 7.2 主要配置项
- `SECRET_KEY`：安全密钥
- `SQLALCHEMY_DATABASE_URI`：数据库连接字符串
- `UPLOAD_FOLDER`：文件上传目录
- `ALLOWED_EXTENSIONS`：允许上传的文件类型
- `MAX_CONTENT_LENGTH`：最大上传文件大小

## 8. 故障排查

### 8.1 常见问题
- **数据库连接失败**：检查数据库连接字符串和网络连接
- **文件上传失败**：检查文件大小和类型是否符合要求
- **权限错误**：确保应用有足够的权限访问文件系统
- **依赖缺失**：运行 `pip install -r requirements.txt` 安装所有依赖

### 8.2 日志查看
- 本地开发：查看控制台输出
- Vercel部署：查看Vercel控制台的部署日志

## 9. 开发指南

### 9.1 代码风格
- 遵循PEP 8代码风格
- 使用有意义的变量和函数命名
- 添加适当的注释

### 9.2 新增功能
1. 在 `routes/` 目录创建新的蓝图文件
2. 在 `templates/` 目录创建对应的模板文件
3. 在 `app.py` 中注册新的蓝图
4. 运行测试确保功能正常

### 9.3 测试
- 运行 `python test_flask_app.py` 进行基本测试
- 运行 `python test_import.py` 测试Excel导入功能

## 10. 版本历史

### 1.0.0 (2025-12-21)
- 初始版本
- 实现了所有核心功能模块
- 支持本地和Vercel部署

## 11. 联系方式

- **开发团队**：宁夏石化公司电仪中心仪表四班
- **项目维护**：系统管理员

---

本文档由系统自动生成，如有疑问请联系系统管理员。