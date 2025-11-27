# 基于YOLO目标检测与DeepSeek分析的作物病害检测系统

## 📋 项目概述

本项目是一个基于YOLO目标检测与DeepSeek分析的低成本、高精度、易部署的作物病害检测系统，支持从病害识别到报告生成的完整闭环，助力农业数字化转型。

## 🎯 项目目标

1. **改进YOLO模型**：开发准确的作物病害检测模型，使用准确率、召回率等指标评估性能
2. **系统集成**：基于Spring Boot + Flask框架，集成YOLO模型和DeepSeek API
3. **完整闭环**：实现从图像上传、病害检测到分析报告生成的完整流程

## 🗂️ 项目结构

```
毕业设计/
├── ai-service/           # AI模型服务 (Flask)
│   ├── app_yolo.py      # YOLO检测服务
│   ├── requirements.txt # Python依赖
│   └── utils/           # 工具函数
├── backend/             # 后端服务 (Spring Boot)
│   ├── src/main/java/   # Java源码
│   └── pom.xml          # Maven配置
├── frontend/            # 前端界面 (Vue.js)
│   ├── src/             # 前端源码
│   └── package.json     # Node.js依赖
├── model-training/      # 模型训练代码
├── models/              # 训练好的模型文件
├── docker/              # Docker部署配置
└── docs/                # 文档
```

## 🚀 快速开始

### 1. 环境准备
```bash
# 安装Python依赖
cd ai-service
pip install -r requirements.txt

# 启动后端服务
cd backend
mvn spring-boot:run

# 启动前端服务
cd frontend
npm install
npm run dev
```

### 2. 数据集配置
数据集位置：`F:\photos\Data for Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network\Plant_leaf_diseases_dataset_with_augmentation\Plant_leave_diseases_dataset_with_augmentation`

### 3. 服务启动
- AI服务：http://localhost:5000
- 后端API：http://localhost:8080
- 前端界面：http://localhost:3000

## 📊 支持的病害类别

系统支持38种植物病害检测，包括：
- 苹果病害：黑星病、黑腐病、锈病等
- 玉米病害：灰斑病、普通锈病、北方叶枯病等
- 葡萄病害：黑腐病、白粉病等
- 番茄病害：细菌性斑点病、早疫病、晚疫病等
- 其他作物：土豆、辣椒、草莓、柑橘等

## 🛠️ 技术栈

- **AI模型**：YOLO v8/v11 + PyTorch
- **后端**：Spring Boot + MySQL
- **前端**：Vue.js + Element Plus
- **AI分析**：DeepSeek API
- **部署**：Docker + Docker Compose

## 📈 开发进度

- [x] 项目框架搭建
- [ ] YOLO模型训练与优化
- [ ] Spring Boot后端开发
- [ ] Vue.js前端开发
- [ ] DeepSeek API集成
- [ ] 系统测试与优化
- [ ] 论文撰写

## 📝 使用说明

1. 上传植物叶片图像
2. 系统自动进行病害检测
3. 生成检测结果和置信度
4. 基于DeepSeek生成分析报告
5. 提供防治建议和趋势分析

## 🤝 贡献指南

本项目为毕业设计项目，欢迎提出建议和意见。

## 📄 许可证

本项目仅用于学术研究和毕业设计。
