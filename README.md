# 🌱 基于YOLO目标检测与DeepSeek分析的作物病害检测系统

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Java-17+-orange.svg" alt="Java">
  <img src="https://img.shields.io/badge/Spring%20Boot-3.1.0-green.svg" alt="Spring Boot">
  <img src="https://img.shields.io/badge/YOLO-v8-red.svg" alt="YOLO">
  <img src="https://img.shields.io/badge/License-Academic-yellow.svg" alt="License">
</p>

## 📋 项目概述

本项目是一个基于 **YOLO 深度学习** 与 **DeepSeek AI** 的智能作物病害检测系统，实现低成本、高精度、易部署的农业病害诊断方案，支持从病害识别到报告生成的完整闭环，助力农业数字化转型。

### ✨ 核心特性

- 🔍 **智能检测**：基于 YOLOv8 的高精度病害识别，支持 **39 种** 作物病害
- 🤖 **AI 分析**：集成 DeepSeek API，提供专业治疗建议和分析报告
- 📊 **数据管理**：完整的用户管理和检测历史记录功能
- 🚀 **易于部署**：支持本地部署和 Docker 容器化部署
- 🌐 **前后端分离**：Spring Boot + Flask + Vue.js 现代化架构

## 🎯 项目目标

1. **改进YOLO模型**：开发准确的作物病害检测模型，使用准确率、召回率等指标评估性能
2. **系统集成**：基于 Spring Boot + Flask 框架，集成 YOLO 模型和 DeepSeek API
3. **完整闭环**：实现从图像上传、病害检测到分析报告生成的完整流程

## 🗂️ 项目结构

```
毕业设计/
├── 📁 ai-service/              # AI 模型服务 (Flask + YOLO)
│   ├── app_production.py       # 生产环境主程序
│   ├── crop_disease_yolo.pt    # 训练好的 YOLO 模型
│   └── requirements.txt        # Python 依赖
├── 📁 backend/                  # 后端服务 (Spring Boot)
│   ├── src/main/java/          # Java 源码
│   │   └── com/graduation/cropdisease/
│   │       ├── controller/     # 控制器层
│   │       ├── service/        # 服务层
│   │       ├── entity/         # 实体类
│   │       └── repository/     # 数据访问层
│   └── pom.xml                 # Maven 配置
├── 📁 frontend/                 # 前端界面 (Vue.js)
├── 📁 model-training/           # 模型训练代码
├── 📁 docker/                   # Docker 部署配置
├── 📁 docs/                     # 项目文档
│   ├── 使用指南.md              # 详细使用指南
│   └── 详细开发计划.md
├── 📁 scripts/                  # 启动脚本
└── 📁 uploads/                  # 上传文件存储
```

## 🚀 快速开始

### 环境要求

| 软件 | 版本 | 必需 |
|------|------|------|
| Python | 3.8+ | ✅ |
| Java JDK | 17+ | ✅ |
| Maven | 3.6+ | ✅ |
| Node.js | 16+ | ⬜ |

### 一键启动

```powershell
# 1. 启动 AI 服务（终端 1）
cd ai-service
pip install -r requirements.txt
python app_production.py

# 2. 启动后端服务（终端 2）
cd backend
mvn spring-boot:run
```

### 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 🤖 AI 检测界面 | http://localhost:5000 | 上传图片进行病害检测 |
| 🔧 后端 API | http://localhost:8080 | REST API 服务 |
| 💚 健康检查 | http://localhost:8080/api/system/health | 系统状态监控 |
| 🗄️ 数据库控制台 | http://localhost:8080/h2-console | H2 数据库管理 |

## 📊 支持的病害类别

系统支持 **39 种** 植物病害检测，覆盖主要农作物：

| 作物 | 支持病害 |
|------|----------|
| 🍎 苹果 | 黑星病、黑腐病、雪松苹果锈病、健康 |
| 🍇 葡萄 | 黑腐病、轮斑病、白粉病、健康 |
| 🍅 番茄 | 细菌性斑点病、早疫病、晚疫病、叶霉病、黄叶曲叶病、花叶病毒等 |
| 🌽 玉米 | 灰斑病、普通锈病、北方叶枯病、健康 |
| 🥔 土豆 | 早疫病、晚疫病、健康 |
| 其他 | 草莓、樱桃、辣椒、柑橘、大豆、南瓜、树莓等 |

## 🛠️ 技术栈

### 后端技术
- **Spring Boot 3.1** - Java Web 框架
- **Spring Data JPA** - 数据持久化
- **H2 Database** - 开发环境数据库
- **MySQL 8.0** - 生产环境数据库

### AI 技术
- **YOLOv8** - 目标检测模型
- **PyTorch** - 深度学习框架
- **Flask** - Python Web 框架
- **DeepSeek API** - AI 分析服务

### 前端技术
- **Vue.js 3** - 前端框架
- **Element Plus** - UI 组件库
- **Axios** - HTTP 客户端

## 📚 API 接口

### 系统接口
```
GET  /api/system/health    # 健康检查
GET  /api/system/info      # 系统信息
```

### 用户接口
```
GET  /api/users            # 获取所有用户
POST /api/users            # 创建用户
POST /api/users/login      # 用户登录
```

### 检测接口
```
GET  /api/detections       # 获取所有记录
POST /api/detections       # 创建检测记录
GET  /api/detections/user/{userId}  # 获取用户记录
```

### AI 检测接口
```
POST /detect               # 图片检测（Form Data）
POST /detect_base64        # Base64 图片检测
GET  /api/classes          # 获取支持的类别
```

## 📈 开发进度

- [x] 项目框架搭建
- [x] YOLO 模型训练（39 类病害）
- [x] AI 服务开发（Flask + YOLO）
- [x] Spring Boot 后端开发
- [ ] Vue.js 前端开发
- [ ] DeepSeek API 深度集成
- [ ] 系统测试与优化
- [ ] Docker 部署配置
- [ ] 论文撰写

## 📖 详细文档

- 📘 [使用指南](docs/使用指南.md) - 完整的安装和使用说明
- 📗 [开发计划](docs/详细开发计划.md) - 项目开发时间线
- 📙 [任务追踪](docs/任务追踪表.md) - 开发任务进度

## 🤝 贡献指南

本项目为毕业设计项目，欢迎提出建议和意见。

## 📄 许可证

本项目仅用于学术研究和毕业设计。

---

<p align="center">
  <b>🌾 智慧农业 · 科技助农 🌾</b>
</p>

