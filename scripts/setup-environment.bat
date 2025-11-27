@echo off
chcp 65001
title 作物病害检测系统 - 环境设置

echo.
echo ============================================
echo    🌱 作物病害检测系统 - 环境设置
echo ============================================
echo.

echo 📋 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.8+: https://www.python.org/downloads/
    pause
    exit /b 1
) else (
    echo ✅ Python已安装
    python --version
)

echo.
echo 📋 检查Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js未安装或未添加到PATH
    echo 请先安装Node.js: https://nodejs.org/
    pause
    exit /b 1
) else (
    echo ✅ Node.js已安装
    node --version
)

echo.
echo 📋 检查Java环境...
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Java未安装或未添加到PATH
    echo 请先安装Java 11+: https://openjdk.org/
    pause
    exit /b 1
) else (
    echo ✅ Java已安装
    java -version
)

echo.
echo 📋 检查Maven环境...
mvn --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Maven未安装或未添加到PATH
    echo 请先安装Maven: https://maven.apache.org/download.cgi
    pause
    exit /b 1
) else (
    echo ✅ Maven已安装
    mvn --version
)

echo.
echo 🔄 开始安装Python依赖...

echo.
echo 📦 安装AI服务依赖...
cd ai-service
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ AI服务依赖安装失败
    pause
    exit /b 1
)
echo ✅ AI服务依赖安装完成
cd ..

echo.
echo 📦 安装模型训练依赖...
cd model-training
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 模型训练依赖安装失败
    pause
    exit /b 1
)
echo ✅ 模型训练依赖安装完成
cd ..

echo.
echo 📦 安装前端依赖...
cd frontend
npm install
if %errorlevel% neq 0 (
    echo ❌ 前端依赖安装失败
    pause
    exit /b 1
)
echo ✅ 前端依赖安装完成
cd ..

echo.
echo 📦 编译后端项目...
cd backend
mvn clean compile
if %errorlevel% neq 0 (
    echo ❌ 后端编译失败
    pause
    exit /b 1
)
echo ✅ 后端编译完成
cd ..

echo.
echo 📋 创建必要目录...
mkdir models 2>nul
mkdir model-training\outputs 2>nul
mkdir uploads 2>nul
echo ✅ 目录创建完成

echo.
echo 🎯 环境设置完成！
echo.
echo 📂 项目结构:
echo   - ai-service/     AI模型服务
echo   - backend/        Spring Boot后端
echo   - frontend/       Vue.js前端
echo   - model-training/ 模型训练脚本
echo   - models/         训练好的模型
echo.
echo 🚀 下一步:
echo   1. 运行数据集分析: python model-training/analyze_dataset.py
echo   2. 训练YOLO模型: python model-training/train_yolo.py
echo   3. 启动服务: 查看 README.md
echo.
pause
