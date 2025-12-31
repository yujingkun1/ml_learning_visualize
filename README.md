# 🤖 ML Learner - 机器学习算法学习平台

一个基于 Vue.js + Flask + MySQL 的机器学习算法学习平台，采用交互式可视化方式帮助用户掌握机器学习和AI算法。

## ✨ 主要特性

### 🎯 核心功能
- **交互式知识图谱**：可视化展示机器学习算法的层次结构
- **算法详细学习**：包含理论讲解、可视化演示、源码实现和相关资源
- **智能推荐系统**：基于学习记录的个性化算法推荐
- **社区交流**：帖子发布、评论、点赞、收藏等社交功能
- **学习进度追踪**：记录学习进度，生成知识掌握雷达图
- **管理员面板**：完整的后台管理功能

### 🧠 算法覆盖
- 监督学习：线性回归、逻辑回归、决策树、随机森林等
- 无监督学习：K-means聚类、主成分分析、t-SNE等
- 深度学习：CNN、RNN、GNN、生成对抗网络等
- 集成学习：随机森林、梯度提升等
- 强化学习：Q-learning、策略梯度等

### 🎨 设计特色
- **Hugging Face 风格**：现代化的UI设计，简洁美观
- **响应式布局**：完美适配桌面和移动设备
- **实时可视化**：使用 ECharts 和 D3.js 提供丰富的图表展示
- **Markdown 支持**：支持富文本内容展示

## 🛠️ 技术栈

### 前端
- **Vue 3** + **TypeScript**：现代前端框架
- **Vite**：快速构建工具
- **Vue Router**：路由管理
- **Pinia**：状态管理
- **D3.js**：知识图谱可视化
- **ECharts**：算法可视化图表
- **Axios**：HTTP 客户端

### 后端
- **Flask**：轻量级 Python Web 框架
- **SQLAlchemy**：ORM 数据库操作
- **Flask-Login**：用户认证
- **JWT**：Token 认证
- **SQLite/MySQL**：数据库

### 数据库设计
- **多对多关系**：用户-算法学习记录，用户-帖子收藏等
- **完整日志系统**：记录所有用户操作和数据库变更
- **角色权限管理**：普通用户和管理员权限区分

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- SQLite (开发环境) 或 MySQL (生产环境)

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd ml-learner
```

2. **后端设置**
```bash
cd backend
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py

# 启动后端服务
python app.py
```

3. **前端设置**
```bash
cd frontend
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

4. **访问应用**
- 前端：http://localhost:5173
- 后端API：http://localhost:5001

### 🚀 一键启动 (推荐)

项目提供了便捷的启动脚本，支持一键启动整个应用：

```bash
# 完整启动（包含数据库初始化）
./start.sh

# 跳过数据库初始化（快速启动）
SKIP_DB_INIT=true ./start.sh

# 自定义端口
PORT=8000 ./start.sh

# 停止服务
./start.sh stop

# 重启服务
./start.sh restart
```

**环境变量说明：**
- `PORT=端口号`：设置后端服务端口（默认：5001）
- `SKIP_DB_INIT=true`：跳过数据库初始化，直接启动服务

**注意：** 首次运行时需要初始化数据库，之后可以使用 `SKIP_DB_INIT=true` 来加速启动。

### 数据库配置

#### 开发环境 (SQLite)
项目默认使用 SQLite，无需额外配置。

#### 生产环境 (MySQL)
设置环境变量：
```bash
export DATABASE_USER=ml_user
export DATABASE_PASSWORD='Yjk381088#'
export DATABASE_HOST=127.0.0.1
export DATABASE_PORT=3306
export DATABASE_NAME=ml_learner
export USE_SQLITE=false
```

## 📊 数据库模式

### 核心表结构
- **users**：用户表（支持管理员角色）
- **algorithms**：算法表
- **algorithm_categories**：算法分类表（层级结构）
- **user_knowledge**：用户学习记录（多对多关系核心）
- **posts**：帖子表
- **comments**：评论表（支持嵌套回复）
- **likes/favorites**：点赞和收藏表
- **system_logs**：系统日志表

### 主要关系
- 用户 ↔ 算法（学习记录）
- 用户 ↔ 帖子（发布、点赞、收藏）
- 算法 ↔ 帖子（相关性关联）
- 帖子 ↔ 评论（层级结构）

## 🔧 API 接口

### 主要端点
- `GET /api/algorithms`：获取算法列表
- `GET /api/categories`：获取分类树
- `POST /api/auth/register`：用户注册
- `POST /api/auth/login`：用户登录
- `GET /api/recommendations`：获取推荐内容
- `GET/POST /api/posts`：帖子CRUD操作
- `POST /api/user/knowledge/{algorithm_id}`：更新学习进度

### 管理员接口
- `GET /api/admin/stats`：获取统计信息
- `GET /api/admin/logs`：查看系统日志
- `DELETE /api/admin/posts/{id}`：删除帖子
- `PUT /api/admin/users/{id}/role`：修改用户角色

## 🎯 使用指南

### 用户操作
1. **浏览知识图谱**：在首页查看算法层次结构
2. **学习算法**：点击节点进入详细学习页面
3. **进度追踪**：在个人中心查看学习进度和雷达图
4. **参与社区**：发布帖子、评论交流
5. **个性化推荐**：系统根据学习记录推荐内容

### 管理员操作
1. **内容管理**：审核和管理用户帖子
2. **用户管理**：修改用户角色，删除违规用户
3. **系统监控**：查看操作日志和统计信息
4. **数据维护**：管理算法和分类数据

## 🔒 安全特性

- **JWT 认证**：安全的 Token 认证机制
- **密码加密**：使用 Werkzeug 进行密码哈希
- **权限控制**：基于角色的访问控制
- **操作日志**：完整的用户操作审计日志
- **输入验证**：前后端双重数据验证

## 📈 性能优化

- **前端优化**：组件懒加载、代码分割
- **后端优化**：数据库查询优化、分页加载
- **缓存策略**：静态资源缓存、API响应缓存
- **可视化优化**：避免重度计算，使用轻量级替代方案

## 🚀 部署说明

### 开发环境
```bash
# 后端
cd backend && python app.py

# 前端
cd frontend && npm run dev
```

### 生产环境
```bash
# 后端
cd backend
export FLASK_ENV=production
python app.py

# 前端构建
cd frontend
npm run build

# 使用 Nginx 提供静态文件
```

### Docker 部署（未来扩展）
```dockerfile
# Dockerfile 示例
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- Vue.js 团队提供的优秀前端框架
- Flask 社区的 Web 框架支持
- ECharts 和 D3.js 的可视化库
- 所有贡献者的宝贵建议

---

**开始你的机器学习学习之旅吧！🚀**

export USE_SQLITE=false
export DATABASE_USER=ml_user
export DATABASE_PASSWORD='Yjk381088#'
export DATABASE_HOST=127.0.0.1
export DATABASE_PORT=3306
export DATABASE_NAME=ml_learner
 
## 本地 Marimo 服务（用于交互演示）

我们通过本地运行的 Marimo 服务来承载交互式 notebook，并将它们嵌入前端的“交互演示”标签页。下面是推荐的本地运行方式与嵌入示例。

1) 在后端虚拟环境中安装 Marimo（已在 backend venv 中安装过一次）：

```
cd backend
source venv/bin/activate
pip install marimo==0.13.1
```

2) 在每个 notebook 的目录启动 Marimo 服务（示例：perceptron）：

```
# 从项目根运行（假设在项目根）
cd perceptron
../../backend/venv/bin/marimo run marimo_notebook.py --host 0.0.0.0 --port 8000 --slug perceptron
```

3) 前端 iframe 嵌入示例（在数据库 `interactive_demo_url` 字段中使用类似 URL）：

```
http://localhost:8000/l/perceptron?show-code=false&embed=true
http://localhost:8000/l/logistic_regression?show-code=false&embed=true
http://localhost:8000/l/gradient_descent?show-code=false&embed=true
```

注意事项：
- "理论讲解"（`notebook_html_url`）与 "交互演示"（`interactive_demo_url`）保持分离。请确保理论栏的 ipynb 嵌入**不要删除**（恢复了被误删的项）。
- 启动 Marimo 服务后，前端会通过 iframe 加载 `interactive_demo_url` 指向的 Marimo 页面，从而实现和原站相同的交互体验但完全本地化。

## 🚀 生产环境部署

本项目支持完整的生产环境部署，包括自动启动、Nginx反向代理、SSL证书配置等。

### 📋 部署前准备

1. **服务器要求**：
   - Ubuntu 20.04+ 或 Debian 11+
   - 至少 2GB RAM，推荐 4GB+
   - 至少 10GB 存储空间
   - Root 或 sudo 权限

2. **域名配置**（推荐）：
   - 已注册域名
   - DNS A记录指向服务器IP

3. **安全注意事项**：
   - 修改默认数据库密码
   - 使用强密码的SECRET_KEY
   - 定期更新系统和依赖

### 🔧 快速部署

#### 方法一：自动部署脚本（推荐）

```bash
# 1. 克隆项目到服务器
git clone https://github.com/yourusername/ml-learner.git /var/www/ml-learner
cd /var/www/ml-learner

# 2. 配置环境变量
cp env.production.template .env.production
nano .env.production  # 编辑数据库密码等敏感信息

# 3. 运行自动部署脚本
sudo ./deploy_production.sh
```

#### 方法二：手动部署

详细的手动部署步骤请参考 [`PRODUCTION_DEPLOYMENT.md`](PRODUCTION_DEPLOYMENT.md) 文件。

### 🔄 从GitHub更新部署

```bash
# 进入项目目录
cd /var/www/ml-learner

# 拉取最新代码
git pull origin main

# 如果后端依赖有更新
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 如果前端有更新
cd ../frontend
npm install
npm run build

# 重启服务
sudo systemctl restart ml-learner
```

### 📊 监控和维护

#### 服务状态检查

```bash
# 检查Flask应用状态
sudo systemctl status ml-learner

# 查看应用日志
sudo journalctl -u ml-learner -f

# 检查Nginx状态
sudo systemctl status nginx
```

#### 备份策略

```bash
# 数据库备份
mysqldump -u ml_user -p ml_learner > backup_$(date +%Y%m%d_%H%M%S).sql

# 代码备份
tar -czf backup_code_$(date +%Y%m%d).tar.gz /var/www/ml-learner
```

### 🔒 安全配置

1. **防火墙配置**：
   ```bash
   sudo ufw allow ssh
   sudo ufw allow 'Nginx Full'
   sudo ufw --force enable
   ```

2. **SSL证书**（推荐）：
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

3. **文件权限**：
   ```bash
   sudo chown -R www-data:www-data /var/www/ml-learner
   sudo chmod 600 /var/www/ml-learner/.env.production
   ```

### 🆘 故障排除

常见问题和解决方案请参考 [`PRODUCTION_DEPLOYMENT.md`](PRODUCTION_DEPLOYMENT.md) 的故障排除章节。

### 📁 部署文件说明

- `deploy_production.sh` - 自动部署脚本
- `start_production.sh` - 生产环境启动脚本
- `nginx.conf` - Nginx配置文件模板
- `ml-learner.service` - Systemd服务文件模板
- `env.production.template` - 环境变量配置模板
- `PRODUCTION_DEPLOYMENT.md` - 详细部署文档

---

**🎉 部署完成后，你的ML Learner学习平台就可以通过域名访问了！**
