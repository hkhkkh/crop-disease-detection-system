# Crop Disease Detection System

基于 YOLO 目标检测与大语言模型的作物病害检测系统。

## 项目简介

本系统使用 YOLOv8 深度学习模型实现作物病害的自动识别，支持 39 种常见作物病害的检测，并集成大语言模型 API 生成治疗建议。

### 主要功能

- 作物病害图像识别（39 类）
- 病害置信度评估
- 治疗方案生成
- 检测历史记录管理
- 用户管理

## 技术栈

**后端**
- Java 17 / Spring Boot 3.1
- Spring Data JPA
- H2 Database（开发）/ MySQL 8.0（生产）

**AI 服务**
- Python 3.10
- Flask
- PyTorch / Ultralytics YOLOv8
- OpenCV

**前端**
- Vue.js 3
- Element Plus

## 项目结构

```
├── ai-service/              # AI 检测服务
│   ├── app_production.py    # Flask 主程序
│   ├── crop_disease_yolo.pt # YOLO 模型
│   └── requirements.txt
├── backend/                 # Spring Boot 后端
│   ├── src/main/java/
│   │   └── com/graduation/cropdisease/
│   │       ├── controller/
│   │       ├── service/
│   │       ├── entity/
│   │       └── repository/
│   └── pom.xml
├── frontend/                # Vue.js 前端
├── model-training/          # 模型训练代码
├── docker/                  # Docker 配置
└── docs/                    # 文档
```

## 快速开始

### 环境要求

- Python 3.8+
- Java 17+
- Maven 3.6+

### 启动 AI 服务

```bash
cd ai-service
pip install -r requirements.txt
python app_production.py
```

服务地址：http://localhost:5000

### 启动后端服务

```bash
cd backend
mvn spring-boot:run
```

服务地址：http://localhost:8080

## API 接口

### 系统接口

```
GET  /api/system/health     # 健康检查
GET  /api/system/info       # 系统信息
```

### 用户接口

```
GET  /api/users             # 获取用户列表
POST /api/users             # 创建用户
POST /api/users/login       # 用户登录
```

### 检测接口

```
GET  /api/detections        # 获取检测记录
POST /api/detections        # 创建检测记录
GET  /api/detections/user/{userId}  # 获取用户检测记录
```

### AI 检测接口

```
POST /detect                # 图片检测
POST /detect_base64         # Base64 图片检测
GET  /api/classes           # 获取支持的类别
```

## 支持的病害类别

系统支持 39 种作物病害识别，包括：

- 苹果：黑星病、黑腐病、雪松苹果锈病
- 葡萄：黑腐病、轮斑病、白粉病
- 番茄：细菌性斑点病、早疫病、晚疫病、叶霉病、黄叶曲叶病
- 玉米：灰斑病、普通锈病、北方叶枯病
- 土豆：早疫病、晚疫病
- 其他：草莓、樱桃、辣椒、柑橘、大豆、南瓜等

## 配置说明

### AI 服务配置

修改 `ai-service/app_production.py` 中的配置项。

### 后端配置

修改 `backend/src/main/resources/application.properties`：

```properties
# 服务端口
server.port=8080

# AI 服务地址
ai.service.url=http://localhost:5000

# 数据库配置（MySQL）
spring.datasource.url=jdbc:mysql://localhost:3306/cropdisease
spring.datasource.username=root
spring.datasource.password=password
```

## 文档

- [使用指南](docs/使用指南.md)
- [开发计划](docs/详细开发计划.md)

## License

MIT

