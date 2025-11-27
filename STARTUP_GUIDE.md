# 🌱 作物病害检测系统 - 启动指南

## 📋 系统要求

### 环境要求
- **Python**: 3.8+ (推荐 3.10+)
- **Java**: 17+
- **Maven**: 3.6+
- **Node.js**: 16+ (可选，用于前端开发)

## 🚀 快速启动

### 第一步：安装 Python 依赖

```bash
# 进入 AI 服务目录
cd ai-service

# 创建虚拟环境（推荐）
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 第二步：启动 AI 服务

```bash
cd ai-service
python app_production.py
```

服务将在 http://localhost:5000 启动

### 第三步：启动后端服务

打开新的终端窗口：

```bash
cd backend
mvn spring-boot:run
```

服务将在 http://localhost:8080 启动

### 第四步：访问系统

- **AI 服务界面**: http://localhost:5000 (直接上传图片进行检测)
- **后端 API**: http://localhost:8080/api/system/health (健康检查)
- **前端界面**: 直接打开 `frontend/index.html`

## 📁 项目结构说明

```
毕业设计/
├── ai-service/                 # AI 检测服务 (Flask + YOLO)
│   ├── app_production.py       # 主服务文件
│   ├── crop_disease_yolo.pt    # 训练好的模型文件
│   └── requirements.txt        # Python 依赖
├── backend/                    # 后端服务 (Spring Boot)
│   ├── src/main/java/          # Java 源码
│   ├── src/main/resources/     # 配置文件
│   └── pom.xml                 # Maven 配置
├── frontend/                   # 前端界面
│   └── index.html              # 主页面
├── model-training/             # 模型训练代码
│   ├── train_yolo.py           # 训练脚本
│   └── yolo_dataset/           # 数据集配置
└── scripts/                    # 辅助脚本
    └── setup-environment.bat   # 环境配置脚本
```

## 🔧 常见问题

### 1. 模块未找到错误
```
ModuleNotFoundError: No module named 'ultralytics'
```
**解决方案**: 运行 `pip install ultralytics flask flask-cors pillow`

### 2. 模型文件未找到
```
⚠️ 未找到训练模型
```
**解决方案**: 确保 `ai-service/crop_disease_yolo.pt` 文件存在

### 3. 端口被占用
```
Address already in use
```
**解决方案**: 关闭占用端口的程序，或修改配置使用其他端口

### 4. Java 版本不兼容
```
Unsupported class file major version
```
**解决方案**: 确保使用 Java 17 或更高版本

## 📊 API 接口说明

### AI 服务接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 主页 - 图片上传界面 |
| `/health` | GET | 健康检查 |
| `/detect` | POST | 病害检测 (表单上传图片) |
| `/classes` | GET | 获取支持的类别列表 |
| `/model/info` | GET | 获取模型信息 |

### 后端服务接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/system/health` | GET | 系统健康检查 |
| `/api/system/info` | GET | 系统信息 |
| `/api/detections` | GET | 获取检测记录 |
| `/api/users` | GET | 获取用户列表 |

## 🎯 支持的病害类别 (39种)

- **苹果**: 黑星病、黑腐病、锈病、健康
- **蓝莓**: 健康
- **樱桃**: 白粉病、健康
- **玉米**: 灰斑病、普通锈病、北方叶枯病、健康
- **葡萄**: 黑腐病、黑痘病、叶斑病、健康
- **柑橘**: 黄龙病
- **桃**: 细菌性斑点病、健康
- **甜椒**: 细菌性斑点病、健康
- **土豆**: 早疫病、晚疫病、健康
- **覆盆子**: 健康
- **大豆**: 健康
- **南瓜**: 白粉病
- **草莓**: 叶焦病、健康
- **番茄**: 细菌性斑点病、早疫病、晚疫病、叶霉病、斑枯病、红蜘蛛、靶斑病、黄化曲叶病毒病、花叶病毒病、健康

## 📝 开发说明

### 模型训练
如需重新训练模型，请参考 `model-training/train_yolo.py`

### 数据库配置
- 默认使用 H2 内存数据库 (开发测试)
- 生产环境可切换到 MySQL，修改 `application.properties`

## 📧 联系方式

如有问题，请提交 Issue 或联系作者。
