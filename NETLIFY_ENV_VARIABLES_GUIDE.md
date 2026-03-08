# Netlify环境变量配置指南

为了确保应用在Netlify上正常运行，您需要设置以下环境变量：

## 必要的环境变量

### 1. SECRET_KEY
- **用途**：用于Flask应用的CSRF保护和会话管理
- **示例值**：`your-secure-random-secret-key`
- **注意事项**：
  - 必须设置一个强随机值
  - 不要在代码或版本控制系统中暴露此值
  - 可以使用以下命令生成一个安全的密钥：
    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

### 2. DATABASE_URL
- **用途**：指定外部数据库连接URL
- **注意事项**：
  - **SQLite在Netlify上不可用**：由于Netlify的无服务器环境使用临时文件系统，SQLite数据库将在每次函数调用后丢失数据
  - **必须使用外部数据库**：推荐使用PostgreSQL或MySQL
- **PostgreSQL示例**：
  ```
  postgresql://username:password@host:port/database
  ```
- **MySQL示例**：
  ```
  mysql+pymysql://username:password@host:port/database
  ```

## 可选的环境变量

### 3. MAX_CONTENT_LENGTH
- **用途**：限制文件上传大小
- **默认值**：16MB (16777216字节)
- **示例值**：`16777216`

### 4. CLOUD_STORAGE_TYPE
- **用途**：指定文件存储类型
- **默认值**：`local`
- **可选值**：`local`, `aws_s3`, `cloudinary`
- **注意事项**：
  - `local`在Netlify上不可靠，因为文件系统是临时的
  - 如果需要持久化存储上传的文件，推荐使用`aws_s3`或`cloudinary`

### 5. AWS S3配置（仅当使用AWS S3存储时）
- **AWS_ACCESS_KEY_ID**：您的AWS访问密钥ID
- **AWS_SECRET_ACCESS_KEY**：您的AWS秘密访问密钥
- **AWS_S3_BUCKET**：您的S3存储桶名称
- **AWS_S3_REGION**：S3存储桶所在的区域（例如：us-east-1）

### 6. Cloudinary配置（仅当使用Cloudinary存储时）
- **CLOUDINARY_CLOUD_NAME**：您的Cloudinary云名称
- **CLOUDINARY_API_KEY**：您的Cloudinary API密钥
- **CLOUDINARY_API_SECRET**：您的Cloudinary API秘密

## 如何在Netlify中设置环境变量

1. 登录到Netlify控制台
2. 选择您的站点
3. 导航到**Site settings** > **Environment variables**
4. 点击**Add a variable**按钮
5. 输入环境变量名称和值
6. 点击**Save**保存

## 注意事项

- 所有敏感信息（如密钥、密码）都应通过环境变量设置，而不是硬编码在代码中
- 在Netlify中设置环境变量后，您需要重新部署应用以应用更改
- 如果使用外部数据库，确保数据库服务器允许来自Netlify的连接（可能需要配置防火墙规则）
- 如果使用云存储服务，确保正确配置了存储桶/容器的访问权限