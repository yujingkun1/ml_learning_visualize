# ML Learner 生产环境部署指南

本文档介绍如何将ML Learner项目部署到生产环境服务器。

## 📋 前置要求

### 服务器要求
- Ubuntu 20.04+ 或 Debian 11+
- 至少 2GB RAM
- 至少 10GB 存储空间
- Root 或 sudo 权限

### 网络要求
- 已注册域名（可选，但推荐用于生产环境）
- 服务器的 80 和 443 端口开放

### 知识要求
- 基本的Linux命令行操作
- MySQL数据库基础知识

## 🚀 快速部署

### 步骤 1: 准备服务器

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要工具
sudo apt install -y git curl
```

### 步骤 2: 下载项目

```bash
# 克隆项目（替换为你的GitHub仓库地址）
git clone https://github.com/yourusername/ml-learner.git /var/www/ml-learner
cd /var/www/ml-learner
```

### 步骤 3: 配置环境变量

```bash
# 复制环境变量模板
cp env.production.template .env.production

# 编辑环境变量文件
nano .env.production
```

在 `.env.production` 文件中配置以下变量：

```bash
# Flask配置
FLASK_ENV=production
SECRET_KEY=your-very-secure-random-secret-key-here

# 数据库配置
DATABASE_USER=ml_user
DATABASE_PASSWORD=your_secure_mysql_password
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=ml_learner

# 服务器配置
PORT=8000
HOST=127.0.0.1
```

### 步骤 4: 运行自动部署脚本

```bash
# 运行部署脚本（需要root权限）
sudo ./deploy_production.sh
```

### 步骤 5: 手动配置数据库

如果自动脚本未能正确导入数据库，请手动执行：

```bash
# 登录MySQL
sudo mysql -u root -p

# 创建数据库和用户
CREATE DATABASE ml_learner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ml_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON ml_learner.* TO 'ml_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 导入数据库
mysql -u ml_user -p ml_learner < database_backup/your_database_dump.sql
```

## 🔧 手动部署步骤（详细版）

如果自动脚本遇到问题，可以按以下步骤手动部署：

### 1. 安装系统依赖

```bash
sudo apt install -y \
    python3 python3-pip python3-venv \
    nginx mysql-server mysql-client \
    git curl build-essential libmysqlclient-dev pkg-config
```

### 2. 设置Python环境

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn pymysql
```

### 3. 配置Nginx

```bash
# 复制nginx配置文件
sudo cp ../nginx.conf /etc/nginx/sites-available/ml-learner

# 编辑配置文件，更新路径
sudo nano /etc/nginx/sites-available/ml-learner

# 创建符号链接
sudo ln -s /etc/nginx/sites-available/ml-learner /etc/nginx/sites-enabled/

# 删除默认配置
sudo rm /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重启nginx
sudo systemctl restart nginx
```

### 4. 配置Systemd服务

```bash
# 复制服务文件
sudo cp ../ml-learner.service /etc/systemd/system/

# 编辑服务文件，更新路径
sudo nano /etc/systemd/system/ml-learner.service

# 重新加载systemd
sudo systemctl daemon-reload

# 启用并启动服务
sudo systemctl enable ml-learner
sudo systemctl start ml-learner
```

### 5. 配置SSL证书（可选）

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 🔍 故障排除

### 检查服务状态

```bash
# 检查Flask应用状态
sudo systemctl status ml-learner

# 查看应用日志
sudo journalctl -u ml-learner -f

# 检查Nginx状态
sudo systemctl status nginx

# 查看Nginx日志
sudo tail -f /var/log/nginx/error.log
```

### 常见问题

#### 数据库连接问题
- 确保MySQL服务正在运行：`sudo systemctl status mysql`
- 检查数据库用户权限
- 验证环境变量配置

#### 端口占用问题
- 检查端口是否被占用：`sudo netstat -tlnp | grep :8000`
- 修改端口配置如果需要

#### 权限问题
- 确保项目目录权限正确：`sudo chown -R www-data:www-data /var/www/ml-learner`
- 检查日志文件权限

#### 前端构建问题
```bash
cd frontend
npm install
npm run build
```

## 📊 监控和维护

### 日志监控

```bash
# 应用日志
sudo journalctl -u ml-learner -f

# Nginx访问日志
sudo tail -f /var/log/nginx/access.log

# Nginx错误日志
sudo tail -f /var/log/nginx/error.log
```

### 服务管理

```bash
# 重启应用
sudo systemctl restart ml-learner

# 重启Nginx
sudo systemctl restart nginx

# 重启MySQL
sudo systemctl restart mysql
```

### 备份策略

```bash
# 数据库备份脚本
mysqldump -u ml_user -p ml_learner > backup_$(date +%Y%m%d_%H%M%S).sql

# 代码备份（如果需要）
tar -czf backup_code_$(date +%Y%m%d).tar.gz /var/www/ml-learner
```

## 🔄 更新部署

当代码更新时：

```bash
# 进入项目目录
cd /var/www/ml-learner

# 拉取最新代码
git pull origin main

# 更新Python依赖（如果有变化）
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 重新构建前端（如果有变化）
cd ../frontend
npm install
npm run build

# 重启服务
sudo systemctl restart ml-learner
```

## 📞 技术支持

如果遇到部署问题，请检查：
1. 系统日志：`sudo journalctl -xe`
2. 应用日志：`sudo journalctl -u ml-learner -f`
3. 网络连接：`curl http://localhost:8000/health`
4. 数据库连接：`mysql -u ml_user -p -e "SELECT 1;"`

## 📋 部署清单

- [ ] 服务器准备完成
- [ ] 项目代码已下载
- [ ] 环境变量已配置
- [ ] 数据库已创建并导入
- [ ] Python依赖已安装
- [ ] 前端已构建
- [ ] Nginx已配置
- [ ] Systemd服务已配置
- [ ] SSL证书已配置（可选）
- [ ] 防火墙已配置
- [ ] 应用可正常访问

---

*最后更新：2025年*
