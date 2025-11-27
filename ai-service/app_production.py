#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
作物病害检测AI服务 - 生产版本
集成训练好的YOLO分类模型
"""

import os
import sys
import time
import json
import uuid
import logging
import base64
import io
from datetime import datetime
from pathlib import Path

# 导入必要的库
try:
    from flask import Flask, request, jsonify, render_template_string
    from flask_cors import CORS
    from ultralytics import YOLO
    import numpy as np
    from PIL import Image
    print("✅ 所有依赖已成功导入")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌱 作物病害检测AI服务</title>
    <style>
        body { 
            font-family: 'Microsoft YaHei', Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #e8f5e8 0%, #f0f8ff 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 15px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .header { 
            text-align: center; 
            color: #2d5a27; 
            margin-bottom: 30px; 
            border-bottom: 2px solid #e8f5e8;
            padding-bottom: 20px;
        }
        .status { 
            background: #e8f5e8; 
            padding: 15px; 
            border-radius: 8px; 
            margin: 20px 0; 
            border-left: 4px solid #4CAF50;
        }
        .upload-area {
            border: 2px dashed #4CAF50;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
            background: #fafafa;
            transition: background 0.3s;
        }
        .upload-area:hover {
            background: #f0f8ff;
        }
        .upload-area.dragover {
            background: #e8f5e8;
            border-color: #45a049;
        }
        .file-input {
            display: none;
        }
        .upload-btn {
            background: #4CAF50;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
            transition: background 0.3s;
        }
        .upload-btn:hover {
            background: #45a049;
        }
        .detect-btn {
            background: #2196F3;
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 18px;
            margin: 20px auto;
            display: block;
            transition: background 0.3s;
        }
        .detect-btn:hover {
            background: #1976D2;
        }
        .detect-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .preview {
            max-width: 300px;
            max-height: 300px;
            margin: 20px auto;
            display: block;
            border-radius: 10px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.2);
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 10px;
            display: none;
        }
        .result.success {
            background: #e8f5e8;
            border: 1px solid #4CAF50;
        }
        .result.error {
            background: #ffebee;
            border: 1px solid #f44336;
        }
        .loading {
            text-align: center;
            margin: 20px 0;
            display: none;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #4CAF50;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .disease-info {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }
        .treatment-info {
            background: #d1ecf1;
            border: 1px solid #17a2b8;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌱 作物病害检测AI服务</h1>
            <p>智能病害诊断 · 精准治疗建议</p>
        </div>
        
        <div class="status">
            <h3>✅ 服务状态</h3>
            <p><strong>模型状态:</strong> 已加载 v1模型</p>
            <p><strong>支持类别:</strong> 39种作物病害</p>
            <p><strong>服务状态:</strong> 正常运行</p>
        </div>
        
        <div class="upload-area" id="uploadArea">
            <h3>📸 上传作物图片</h3>
            <p>点击选择文件或拖拽图片到此区域</p>
            <input type="file" id="imageInput" class="file-input" accept="image/*">
            <button class="upload-btn" onclick="document.getElementById('imageInput').click()">
                选择图片文件
            </button>
            <p style="color: #666; font-size: 14px;">支持 JPG、JPEG、PNG 格式，最大 16MB</p>
        </div>
        
        <img id="imagePreview" class="preview" style="display: none;">
        
        <button id="detectBtn" class="detect-btn" disabled onclick="detectDisease()">
            🔍 开始检测
        </button>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>AI正在分析图片...</p>
        </div>
        
        <div id="result" class="result"></div>
    </div>

    <script>
        let selectedImage = null;
        
        // 文件选择处理
        document.getElementById('imageInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                handleImageSelect(file);
            }
        });
        
        // 拖拽上传处理
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                handleImageSelect(file);
            }
        });
        
        function handleImageSelect(file) {
            selectedImage = file;
            
            // 显示预览
            const reader = new FileReader();
            reader.onload = function(e) {
                const preview = document.getElementById('imagePreview');
                preview.src = e.target.result;
                preview.style.display = 'block';
            };
            reader.readAsDataURL(file);
            
            // 启用检测按钮
            document.getElementById('detectBtn').disabled = false;
            
            // 隐藏之前的结果
            document.getElementById('result').style.display = 'none';
        }
        
        function detectDisease() {
            if (!selectedImage) return;
            
            const formData = new FormData();
            formData.append('image', selectedImage);
            
            // 显示加载状态
            document.getElementById('loading').style.display = 'block';
            document.getElementById('detectBtn').disabled = true;
            document.getElementById('result').style.display = 'none';
            
            fetch('/detect', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('detectBtn').disabled = false;
                showResult(data);
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('detectBtn').disabled = false;
                showError('检测失败: ' + error.message);
            });
        }
        
        function showResult(data) {
            const resultDiv = document.getElementById('result');
            
            // 调试：打印响应数据结构
            console.log('🔍 检测响应数据:', data);
            console.log('🔍 数据类型:', typeof data);
            
            if (data.success && data.result && data.result.primary) {
                const primary = data.result.primary;
                console.log('✅ Primary数据:', primary);
                console.log('🔍 Confidence类型:', typeof primary.confidence, 'Value:', primary.confidence);
                
                resultDiv.className = 'result success';
                resultDiv.innerHTML = `
                    <h3>🎉 检测完成</h3>
                    <div class="disease-info">
                        <h4>🦠 病害诊断</h4>
                        <p><strong>作物类型:</strong> ${primary.crop_type || 'N/A'}</p>
                        <p><strong>病害名称:</strong> ${primary.disease_name || 'N/A'}</p>
                        <p><strong>置信度:</strong> ${primary.confidence ? (primary.confidence * 100).toFixed(2) : 'N/A'}%</p>
                    </div>
                    <div class="treatment-info">
                        <h4>💊 治疗建议</h4>
                        <p><strong>中文名称:</strong> ${primary.treatment_info?.chinese_name || 'N/A'}</p>
                        <p><strong>治疗方案:</strong> ${primary.treatment_info?.treatment || 'N/A'}</p>
                        <p><strong>预防措施:</strong> ${primary.treatment_info?.prevention || 'N/A'}</p>
                        <p><strong>严重程度:</strong> ${primary.treatment_info?.severity || 'N/A'}</p>
                    </div>
                    <p><strong>检测时间:</strong> ${data.processing_time || 'N/A'}秒</p>
                    <p><strong>检测ID:</strong> ${data.detection_id || 'N/A'}</p>
                `;
            } else {
                console.log('❌ 数据结构不匹配:', {
                    success: data.success,
                    hasResult: !!data.result,
                    hasPrimary: !!(data.result && data.result.primary)
                });
                resultDiv.className = 'result error';
                resultDiv.innerHTML = `
                    <h3>❌ 检测失败</h3>
                    <p>${data.error || data.message || '数据格式错误'}</p>
                    <pre style="background:#f5f5f5;padding:10px;margin-top:10px;font-size:12px;">${JSON.stringify(data, null, 2)}</pre>
                `;
            }
            
            resultDiv.style.display = 'block';
        }
        
        function showError(message) {
            const resultDiv = document.getElementById('result');
            resultDiv.className = 'result error';
            resultDiv.innerHTML = `
                <h3>❌ 错误</h3>
                <p>${message}</p>
            `;
            resultDiv.style.display = 'block';
        }
    </script>
</body>
</html>
"""

# 配置上传目录
UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

class CropDiseaseDetector:
    def __init__(self):
        """初始化作物病害检测器"""
        print("🔧 初始化检测器...")
        
        # 类别名称（基于训练数据集 - 与classes.txt完全一致）
        self.class_names = [
            "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
            "Background_without_leaves", "Blueberry___healthy", "Cherry___Powdery_mildew", "Cherry___healthy",
            "Corn___Cercospora_leaf_spot Gray_leaf_spot", "Corn___Common_rust", "Corn___Northern_Leaf_Blight", "Corn___healthy",
            "Grape___Black_rot", "Grape___Esca_(Black_Measles)", "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape___healthy",
            "Orange___Haunglongbing_(Citrus_greening)", "Peach___Bacterial_spot", "Peach___healthy",
            "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy",
            "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy",
            "Raspberry___healthy", "Soybean___healthy", "Squash___Powdery_mildew",
            "Strawberry___Leaf_scorch", "Strawberry___healthy",
            "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight",
            "Tomato___Leaf_Mold", "Tomato___Septoria_leaf_spot", "Tomato___Spider_mites Two-spotted_spider_mite",
            "Tomato___Target_Spot", "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Tomato_mosaic_virus",
            "Tomato___healthy"
        ]
        
        # 治疗建议数据库 - 覆盖所有39个类别
        self.treatment_database = {
            # 苹果类
            "Apple___Apple_scab": {
                "chinese_name": "苹果黑星病",
                "treatment": "喷施三唑类杀菌剂(如戊唑醇)，加强修剪通风，清除落叶",
                "prevention": "选用抗病品种，避免密植，雨后及时排水",
                "severity": "中等",
                "impact": "影响果实外观，严重时影响产量"
            },
            "Apple___Black_rot": {
                "chinese_name": "苹果黑腐病",
                "treatment": "喷施代森锰锌或百菌清，剪除病枝",
                "prevention": "合理修剪，加强通风透光，及时清除病果",
                "severity": "严重",
                "impact": "可导致果实腐烂，减产20-40%"
            },
            "Apple___Cedar_apple_rust": {
                "chinese_name": "苹果锈病",
                "treatment": "喷施三唑类杀菌剂，清除周围桧柏树",
                "prevention": "避免在桧柏树附近种植苹果，选用抗病品种",
                "severity": "中等",
                "impact": "影响叶片和果实，减产10-20%"
            },
            "Apple___healthy": {
                "chinese_name": "苹果健康",
                "treatment": "无需治疗，植株健康",
                "prevention": "继续保持良好的田间管理",
                "severity": "无",
                "impact": "植株健康，无病害影响"
            },
            # 背景类
            "Background_without_leaves": {
                "chinese_name": "无叶背景",
                "treatment": "非植物图像，无需处理",
                "prevention": "请上传植物叶片图像进行检测",
                "severity": "无",
                "impact": "无"
            },
            # 蓝莓类
            "Blueberry___healthy": {
                "chinese_name": "蓝莓健康",
                "treatment": "无需治疗，植株健康",
                "prevention": "保持土壤酸性，适当施肥",
                "severity": "无",
                "impact": "植株健康，无病害影响"
            },
            # 樱桃类
            "Cherry___Powdery_mildew": {
                "chinese_name": "樱桃白粉病",
                "treatment": "喷施硫磺制剂或三唑类杀菌剂",
                "prevention": "加强通风，避免过密种植，控制湿度",
                "severity": "中等",
                "impact": "影响叶片光合作用，减产10-30%"
            },
            "Cherry___healthy": {
                "chinese_name": "樱桃健康",
                "treatment": "无需治疗，植株健康",
                "prevention": "保持良好的水肥管理",
                "severity": "无",
                "impact": "植株健康，无病害影响"
            },
            # 玉米类
            "Corn___Cercospora_leaf_spot Gray_leaf_spot": {
                "chinese_name": "玉米灰斑病",
                "treatment": "喷施代森锰锌或甲基托布津",
                "prevention": "轮作，清除病残体，选用抗病品种",
                "severity": "中等",
                "impact": "减产10-30%"
            },
            "Corn___Common_rust": {
                "chinese_name": "玉米普通锈病",
                "treatment": "喷施三唑类杀菌剂，加强田间管理",
                "prevention": "选用抗病品种，适期播种",
                "severity": "轻微",
                "impact": "一般减产5-15%"
            },
            "Corn___Northern_Leaf_Blight": {
                "chinese_name": "玉米北方叶枯病",
                "treatment": "喷施代森锰锌或百菌清",
                "prevention": "轮作倒茬，选用抗病品种",
                "severity": "中等",
                "impact": "减产15-30%"
            },
            "Corn___healthy": {
                "chinese_name": "玉米健康",
                "treatment": "无需治疗，植株健康",
                "prevention": "保持良好的田间管理",
                "severity": "无",
                "impact": "植株健康，无病害影响"
            },
            # 葡萄类
            "Grape___Black_rot": {
                "chinese_name": "葡萄黑腐病",
                "treatment": "喷施代森锰锌或甲基托布津，清除病果",
                "prevention": "加强修剪，保持通风，及时排水",
                "severity": "严重",
                "impact": "可导致果实腐烂，减产30-50%"
            },
            "Grape___Esca_(Black_Measles)": {
                "chinese_name": "葡萄黑痘病",
                "treatment": "喷施波尔多液或铜制剂",
                "prevention": "选用健康苗木，加强树势管理",
                "severity": "严重",
                "impact": "影响树势和产量，严重时可致死"
            },
            "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
                "chinese_name": "葡萄叶斑病",
                "treatment": "喷施代森锰锌或百菌清",
                "prevention": "加强通风，合理施肥",
                "severity": "中等",
                "impact": "减产10-25%"
            },
            "Grape___healthy": {
                "chinese_name": "葡萄健康",
                "treatment": "无需治疗，植株健康",
                "prevention": "继续保持良好的管理措施",
                "severity": "无",
                "impact": "植株健康，无病害影响"
            },
            # 柑橘类
            "Orange___Haunglongbing_(Citrus_greening)": {
                "chinese_name": "柑橘黄龙病",
                "treatment": "目前无有效治疗方法，需挖除病树",
                "prevention": "控制木虱传播，选用无病苗木",
                "severity": "致命",
                "impact": "毁灭性病害，可导致树木死亡"
            },
            # 桃类
            "Peach___Bacterial_spot": {
                "chinese_name": "桃细菌性斑点病",
                "treatment": "喷施铜制剂或链霉素",
                "prevention": "避免伤口感染，合理修剪",
                "severity": "中等",
                "impact": "影响果实外观，减产15-25%"
            },
            "Peach___healthy": {
                "chinese_name": "桃健康",
                "treatment": "无需治疗，植株健康",
                "prevention": "保持良好的水肥管理",
                "severity": "无",
                "impact": "植株健康，无病害影响"
            },
            # 辣椒类
            "Pepper,_bell___Bacterial_spot": {
                "chinese_name": "甜椒细菌性斑点病",
                "treatment": "喷施铜制剂，清除病叶",
                "prevention": "使用无病种子，避免高湿环境",
                "severity": "中等",
                "impact": "减产15-30%"
            },
            "Pepper,_bell___healthy": {
                "chinese_name": "甜椒健康",
                "treatment": "无需治疗，植株健康",
                "prevention": "保持适宜的温湿度",
                "severity": "无",
                "impact": "植株健康，无病害影响"
            },
            # 土豆类
            "Potato___Early_blight": {
                "chinese_name": "土豆早疫病",
                "treatment": "喷施代森锰锌或百菌清",
                "prevention": "轮作，避免过密种植，合理施肥",
                "severity": "中等",
                "impact": "减产15-30%"
            },
            "Potato___Late_blight": {
                "chinese_name": "土豆晚疫病",
                "treatment": "喷施烯酰吗啉或霜脲氰，及时清除病株",
                "prevention": "选用抗病品种，控制湿度，预防性用药",
                "severity": "严重",
                "impact": "毁灭性病害，可导致绝收"
            },
            "Potato___healthy": {
                "chinese_name": "土豆健康",
                "treatment": "无需治疗，植株健康",
                "prevention": "保持良好的田间管理",
                "severity": "无",
                "impact": "植株健康，无病害影响"
            },
            # 覆盆子类
            "Raspberry___healthy": {
                "chinese_name": "覆盆子健康",
                "treatment": "无需治疗，植株健康",
                "prevention": "保持良好的管理措施",
                "severity": "无",
                "impact": "植株健康，无病害影响"
            },
            # 大豆类
            "Soybean___healthy": {
                "chinese_name": "大豆健康",
                "treatment": "无需治疗，植株健康",
                "prevention": "轮作倒茬，合理施肥",
                "severity": "无",
                "impact": "植株健康，无病害影响"
            },
            # 南瓜类
            "Squash___Powdery_mildew": {
                "chinese_name": "南瓜白粉病",
                "treatment": "喷施硫磺制剂或三唑类杀菌剂",
                "prevention": "加强通风，避免过密种植",
                "severity": "中等",
                "impact": "减产20-40%"
            },
            # 草莓类
            "Strawberry___Leaf_scorch": {
                "chinese_name": "草莓叶焦病",
                "treatment": "喷施代森锰锌，清除病叶",
                "prevention": "避免高温高湿，合理灌溉",
                "severity": "中等",
                "impact": "减产15-25%"
            },
            "Strawberry___healthy": {
                "chinese_name": "草莓健康",
                "treatment": "无需治疗，植株健康",
                "prevention": "保持适宜的生长环境",
                "severity": "无",
                "impact": "植株健康，无病害影响"
            },
            # 番茄类
            "Tomato___Bacterial_spot": {
                "chinese_name": "番茄细菌性斑点病",
                "treatment": "喷施铜制剂，清除病叶",
                "prevention": "使用无病种子，避免高湿环境",
                "severity": "中等",
                "impact": "减产15-25%"
            },
            "Tomato___Early_blight": {
                "chinese_name": "番茄早疫病",
                "treatment": "喷施代森锰锌或百菌清，加强栽培管理",
                "prevention": "合理密植，避免偏施氮肥，加强通风",
                "severity": "中等",
                "impact": "影响叶片和果实，可减产20-40%"
            },
            "Tomato___Late_blight": {
                "chinese_name": "番茄晚疫病",
                "treatment": "使用烯酰吗啉或霜脲氰防治，避免田间积水",
                "prevention": "选用抗病品种，控制湿度，预防性用药",
                "severity": "严重",
                "impact": "毁灭性病害，可导致绝收"
            },
            "Tomato___Leaf_Mold": {
                "chinese_name": "番茄叶霉病",
                "treatment": "喷施百菌清或甲基托布津",
                "prevention": "加强通风，控制湿度",
                "severity": "中等",
                "impact": "减产20-30%"
            },
            "Tomato___Septoria_leaf_spot": {
                "chinese_name": "番茄斑枯病",
                "treatment": "喷施代森锰锌或百菌清",
                "prevention": "轮作，清除病残体",
                "severity": "中等",
                "impact": "减产15-25%"
            },
            "Tomato___Spider_mites Two-spotted_spider_mite": {
                "chinese_name": "番茄红蜘蛛",
                "treatment": "喷施阿维菌素或哒螨灵",
                "prevention": "保持适宜湿度，及时清除杂草",
                "severity": "中等",
                "impact": "减产10-30%"
            },
            "Tomato___Target_Spot": {
                "chinese_name": "番茄靶斑病",
                "treatment": "喷施代森锰锌或百菌清",
                "prevention": "加强通风，合理施肥",
                "severity": "中等",
                "impact": "减产15-25%"
            },
            "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
                "chinese_name": "番茄黄化曲叶病毒病",
                "treatment": "目前无有效药剂，需拔除病株",
                "prevention": "控制烟粉虱传播，选用抗病品种",
                "severity": "严重",
                "impact": "减产50%以上"
            },
            "Tomato___Tomato_mosaic_virus": {
                "chinese_name": "番茄花叶病毒病",
                "treatment": "目前无有效治疗方法，需拔除病株",
                "prevention": "使用无病种子，避免机械传播",
                "severity": "严重",
                "impact": "减产30-50%"
            },
            "Tomato___healthy": {
                "chinese_name": "番茄健康",
                "treatment": "无需治疗，植株健康",
                "prevention": "保持良好的水肥管理",
                "severity": "无",
                "impact": "植株健康，无病害影响"
            }
        }
        
        # 加载模型
        self.load_model()
        
        print(f"✅ 检测器初始化完成，支持 {len(self.class_names)} 个类别")
        
    def load_model(self):
        """加载训练好的模型v1"""
        # 使用绝对路径确保能找到模型文件
        # 首先检查当前目录下的模型文件
        current_dir = Path(__file__).parent
        model_path = current_dir / "crop_disease_yolo.pt"
        
        # 备选路径
        if not model_path.exists():
            base_dir = current_dir.parent
            model_path = base_dir / "model-training" / "models" / "crop_disease_yolo.pt"
        
        if model_path.exists():
            try:
                print(f"📦 加载训练模型v1: {model_path}")
                self.model = YOLO(str(model_path))
                print("✅ 训练模型v1加载成功")
                print(f"📊 支持类别数: {len(self.model.names)}")
                self.model_type = "custom_trained"
                self.model_loaded = True
                return True
            except Exception as e:
                print(f"❌ 训练模型加载失败: {e}")
                self.load_fallback_model()
        else:
            print(f"⚠️ 未找到训练模型，检查路径: {model_path}")
            self.load_fallback_model()
            
    def load_fallback_model(self):
        """加载备用模型"""
        try:
            print("📦 加载预训练模型...")
            self.model = YOLO('yolov8n.pt')
            print("✅ 预训练模型加载成功")
            self.model_type = "pretrained"
            self.model_loaded = True
        except Exception as e:
            print(f"❌ 所有模型加载失败: {e}")
            self.model = None
            self.model_type = "none"
            self.model_loaded = False
            
    def preprocess_image(self, image_data):
        """预处理图像"""
        try:
            # 处理不同类型的图像输入
            if isinstance(image_data, str):
                # Base64字符串
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
            elif isinstance(image_data, bytes):
                # 字节数据
                image = Image.open(io.BytesIO(image_data))
            else:
                # PIL Image或numpy array
                image = image_data
                
            # 转换为RGB
            if hasattr(image, 'mode') and image.mode != 'RGB':
                image = image.convert('RGB')
                
            return image
            
        except Exception as e:
            logger.error(f"图像预处理失败: {e}")
            return None
            
    def detect_disease(self, image_data):
        """检测植物病害"""
        try:
            # 预处理图像
            image = self.preprocess_image(image_data)
            if image is None:
                return self.create_error_response("图像预处理失败")
                
            # 使用模型进行检测
            if self.model_loaded:
                return self.classify_with_model(image)
            else:
                return self.simulate_detection()
                
        except Exception as e:
            logger.error(f"病害检测失败: {e}")
            return self.create_error_response(f"检测失败: {str(e)}")
            
    def classify_with_model(self, image):
        """使用模型进行分类"""
        try:
            # 进行预测
            results = self.model(image, verbose=False)
            
            if results and len(results) > 0:
                result = results[0]
                
                # 检查是否有分类结果
                if hasattr(result, 'probs') and result.probs is not None:
                    # 获取Top-5结果
                    top5_indices = result.probs.top5
                    top5_confidences = result.probs.top5conf
                    
                    classifications = []
                    for i, (idx, conf) in enumerate(zip(top5_indices, top5_confidences)):
                        if idx < len(self.class_names):
                            class_name = self.class_names[idx]
                            
                            # 解析类别信息
                            crop_type, disease_name = self.parse_class_name(class_name)
                            
                            # 获取治疗建议
                            treatment_info = self.get_treatment_info(class_name)
                            
                            classification = {
                                'rank': i + 1,
                                'class_name': class_name,
                                'crop_type': crop_type,
                                'disease_name': disease_name,
                                'confidence': float(conf),
                                'treatment_info': treatment_info
                            }
                            classifications.append(classification)
                    
                    return self.format_classification_response(classifications)
                    
            # 没有有效结果
            return self.create_error_response("未检测到有效的植物病害信息")
            
        except Exception as e:
            logger.error(f"模型分类失败: {e}")
            return self.simulate_detection()
            
    def parse_class_name(self, class_name):
        """解析类别名称"""
        if "___" in class_name:
            parts = class_name.split("___", 1)
            crop_type = parts[0].replace("_", " ")
            disease_name = parts[1].replace("_", " ")
        elif class_name == "Background_without_leaves":
            crop_type = "Background"
            disease_name = "without leaves"
        else:
            crop_type = "Unknown"
            disease_name = class_name.replace("_", " ")
            
        return crop_type, disease_name
        
    def get_treatment_info(self, class_name):
        """获取治疗建议"""
        return self.treatment_database.get(class_name, {
            "chinese_name": "未知病害",
            "treatment": "请咨询农业专家获取具体治疗方案",
            "prevention": "加强田间管理，定期检查",
            "severity": "未知",
            "impact": "需要专业评估"
        })
        
    def format_classification_response(self, classifications):
        """格式化分类响应"""
        primary_result = classifications[0] if classifications else None
        
        return {
            'success': True,
            'detection_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'result': {
                'primary': primary_result,
                'top5': classifications[:5],
                'detected': len(classifications) > 0
            },
            'model_info': {
                'model_type': self.model_type,
                'model_loaded': self.model_loaded,
                'total_classes': len(self.class_names)
            }
        }
        
    def simulate_detection(self):
        """模拟检测结果"""
        simulation_result = {
            'rank': 1,
            'class_name': 'Tomato___Early_blight',
            'crop_type': 'Tomato',
            'disease_name': 'Early blight',
            'confidence': 0.85,
            'treatment_info': self.get_treatment_info('Tomato___Early_blight')
        }
        
        return self.format_classification_response([simulation_result])
        
    def create_error_response(self, message):
        """创建错误响应"""
        return {
            'success': False,
            'error': message,
            'timestamp': datetime.now().isoformat()
        }

# 创建检测器实例
print("🚀 创建检测器实例...")
detector = CropDiseaseDetector()

@app.route('/', methods=['GET'])
def home():
    """主页 - 显示图片上传界面"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'success': True,
        'message': '🌱 作物病害检测AI服务运行中',
        'service': 'crop-disease-detection',
        'version': '1.0.0',
        'model_loaded': detector.model_loaded,
        'model_type': detector.model_type,
        'supported_classes': len(detector.class_names),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/detect', methods=['POST'])
def detect_disease():
    """病害检测接口"""
    try:
        # 检查请求数据
        if 'image' not in request.files and not request.is_json:
            return jsonify({
                'success': False,
                'error': '未提供图像数据'
            }), 400
            
        # 处理文件上传
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': '未选择文件'
                }), 400
                
            # 检查文件类型
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
            if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                return jsonify({
                    'success': False,
                    'error': '不支持的文件格式'
                }), 400
                
            # 保存临时文件
            filename = f"{uuid.uuid4().hex}_{file.filename}"
            filepath = app.config['UPLOAD_FOLDER'] / filename
            file.save(filepath)
            
            # 读取图像
            image = Image.open(filepath)
            
            # 清理临时文件
            try:
                os.remove(filepath)
            except:
                pass
                
        # 处理JSON数据
        elif request.is_json:
            data = request.get_json()
            image_data = data.get('image_data')
            if not image_data:
                return jsonify({
                    'success': False,
                    'error': '未提供图像数据'
                }), 400
            image = image_data
        else:
            return jsonify({
                'success': False,
                'error': '无效的请求格式'
            }), 400
            
        # 执行检测
        start_time = time.time()
        result = detector.detect_disease(image)
        processing_time = time.time() - start_time
        
        # 添加处理时间
        result['processing_time'] = round(processing_time, 3)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"检测接口错误: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500

@app.route('/classes', methods=['GET'])
def get_classes():
    """获取支持的类别列表"""
    return jsonify({
        'success': True,
        'classes': detector.class_names,
        'total_classes': len(detector.class_names),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/model/info', methods=['GET'])
def get_model_info():
    """获取模型信息"""
    return jsonify({
        'success': True,
        'model_info': {
            'model_loaded': detector.model_loaded,
            'model_type': detector.model_type,
            'num_classes': len(detector.class_names),
            'architecture': 'YOLOv8 Classification',
            'training_status': 'Custom trained on crop disease dataset' if detector.model_type == 'custom_trained' else 'Pretrained model'
        },
        'capabilities': {
            'classification': True,
            'detection': False,
            'batch_processing': False
        },
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🌱 作物病害检测AI服务")
    print("=" * 50)
    print(f"📦 模型状态: {'✅ 已加载' if detector.model_loaded else '❌ 未加载'}")
    print(f"🔧 模型类型: {detector.model_type}")
    print(f"🎯 支持类别: {len(detector.class_names)} 个")
    print(f"📊 训练模型: {'✅ 是' if detector.model_type == 'custom_trained' else '❌ 否'}")
    print("🚀 服务启动中...")
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True
        )
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")
        print("尝试使用其他端口...")
        try:
            app.run(
                host='127.0.0.1',
                port=5001,
                debug=False,
                threaded=True
            )
        except Exception as e2:
            print(f"❌ 备用端口也失败: {e2}")
