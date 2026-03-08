# Netlify部署指南

## 1. 准备工作

### 1.1 外部数据库设置
由于Netlify的无服务器环境中文件系统是临时的，您需要配置一个外部数据库。推荐使用：
- PostgreSQL (推荐使用Supabase或Neon)
- MySQL (推荐使用PlanetScale)

### 1.2 文件存储设置（可选）
如果您需要文件上传功能，建议配置以下外部存储服务之一：
- AWS S3
- Cloudinary

## 2. 部署步骤

### 2.1 创建Netlify账户
如果您还没有Netlify账户，请访问[Netlify官网](https://www.netlify.com/)注册。

### 2.2 连接GitHub仓库
1. 登录Netlify后，点击"Add new site" → "Import an existing project"
2. 选择您的GitHub仓库
3. 配置部署设置：
   - **Build command**: `pip install -r requirements.txt`
   - **Publish directory**: `static`
   - **Functions directory**: `functions`

### 2.3 配置环境变量
在Netlify控制台中，进入项目的"Site settings" → "Environment variables"，添加以下环境变量：

| 环境变量名 | 描述 | 示例值 |
|------------|------|--------|
| SECRET_KEY | Flask应用的密钥 | `your-secret-key-123` |
| DATABASE_URL | 外部数据库连接URL | `postgresql://user:password@host:port/dbname?sslmode=require` |
| CLOUD_STORAGE_TYPE | 文件存储类型 (local/aws_s3/cloudinary) | `local` |
| AWS_ACCESS_KEY_ID | AWS S3访问密钥ID (如果使用AWS S3) | `AKIA...` |
| AWS_SECRET_ACCESS_KEY | AWS S3秘密访问密钥 (如果使用AWS S3) | `your-secret-key` |
| AWS_S3_BUCKET | AWS S3存储桶名称 (如果使用AWS S3) | `your-bucket-name` |
| AWS_S3_REGION | AWS S3区域 (如果使用AWS S3) | `us-east-1` |
| CLOUDINARY_CLOUD_NAME | Cloudinary云名称 (如果使用Cloudinary) | `your-cloud-name` |
| CLOUDINARY_API_KEY | Cloudinary API密钥 (如果使用Cloudinary) | `123456789` |
| CLOUDINARY_API_SECRET | Cloudinary API密钥 (如果使用Cloudinary) | `your-api-secret` |

### 2.4 触发部署
点击"Deploy site"按钮触发部署。

## 3. 故障排除

### 3.1 404错误解决
如果部署后出现404错误，请检查：
1. 确保`netlify.toml`文件配置正确，特别是重定向规则
2. 检查Netlify函数是否正确部署（在Netlify控制台的"Functions"标签页）
3. 查看部署日志，检查是否有任何错误
4. 确保所有必要的文件都被包含在部署中

### 3.2 数据库连接问题
如果出现数据库连接问题：
1. 确保DATABASE_URL环境变量配置正确
2. 对于PostgreSQL数据库，确保URL以`postgresql://`开头（不是`postgres://`）
3. 检查数据库服务器是否允许来自Netlify的连接

### 3.3 文件上传问题
如果文件上传功能不正常：
1. 确保配置了外部存储服务（AWS S3或Cloudinary）
2. 检查相关环境变量是否配置正确
3. 查看Netlify函数日志，检查是否有任何错误

## 4. 性能优化

### 4.1 静态资源
- 静态资源已经配置为从`static`目录提供
- 可以考虑使用CDN加速静态资源访问

### 4.2 数据库查询
- 确保所有数据库查询都有适当的索引
- 考虑使用缓存减少数据库查询次数

### 4.3 函数优化
- 减少函数的冷启动时间
- 确保只导入必要的模块

## 5. 监控和日志

- 在Netlify控制台的"Functions"标签页查看函数日志
- 使用Netlify的Analytics功能监控网站流量
- 考虑设置错误跟踪服务（如Sentry）

## 6. 注意事项

- Netlify函数有执行时间限制（默认10秒），对于长时间运行的操作可能需要优化
- SQLite数据库在Netlify环境中是临时的，数据会在函数执行结束后丢失
- 文件系统存储也是临时的，上传的文件会在函数执行结束后丢失
- 定期备份外部数据库

## 7. 更新应用

要更新应用：
1. 将更改推送到GitHub仓库
2. Netlify会自动触发新的部署
3. 如果有数据库结构更改，需要手动更新外部数据库

## 8. 联系支持

如果您遇到任何问题，请参考：
- [Netlify文档](https://docs.netlify.com/)
- [Netlify Functions文档](https://docs.netlify.com/functions/overview/)
- [Flask部署到Netlify指南](https://docs.netlify.com/integrations/frameworks/flask/)