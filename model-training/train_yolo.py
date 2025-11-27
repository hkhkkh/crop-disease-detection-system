#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的YOLO作物病害检测模型训练脚本
基于YOLOv8进行作物病害检测模型的训练和优化
"""

import os
import sys
import torch
import yaml
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import cv2
from PIL import Image
import random

# 添加ultralytics支持
try:
    from ultralytics import YOLO
    from ultralytics.utils.plotting import Annotator, colors
except ImportError:
    print("❌ 请安装ultralytics: pip install ultralytics")
    sys.exit(1)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

class CropDiseaseYOLOTrainer:
    def __init__(self, config):
        """初始化YOLO训练器"""
        self.config = config
        self.dataset_path = Path(config['dataset_path'])
        self.output_dir = Path(config['output_dir'])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置随机种子
        self.set_random_seed(config.get('random_seed', 42))
        
        # 类别信息
        self.class_names = []
        self.class_mapping = {}
        
        print(f"🎯 YOLO训练器初始化完成")
        print(f"📂 数据集路径: {self.dataset_path}")
        print(f"📁 输出目录: {self.output_dir}")
        
    def set_random_seed(self, seed):
        """设置随机种子确保结果可复现"""
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
        print(f"🎲 随机种子设置为: {seed}")
        
    def prepare_dataset(self):
        """准备YOLO格式的数据集"""
        print("\n🔄 准备YOLO数据集...")
        
        # 创建YOLO数据集目录结构
        yolo_dir = self.output_dir / "yolo_dataset"
        train_img_dir = yolo_dir / "train" / "images"
        train_label_dir = yolo_dir / "train" / "labels"
        val_img_dir = yolo_dir / "val" / "images"
        val_label_dir = yolo_dir / "val" / "labels"
        test_img_dir = yolo_dir / "test" / "images"
        test_label_dir = yolo_dir / "test" / "labels"
        
        # 创建目录
        for dir_path in [train_img_dir, train_label_dir, val_img_dir, val_label_dir, test_img_dir, test_label_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        # 获取所有类别
        class_dirs = [d for d in self.dataset_path.iterdir() if d.is_dir()]
        self.class_names = sorted([d.name for d in class_dirs])
        self.class_mapping = {name: idx for idx, name in enumerate(self.class_names)}
        
        print(f"📋 发现 {len(self.class_names)} 个类别")
        
        # 处理每个类别的图像
        all_image_paths = []
        all_labels = []
        
        for class_dir in class_dirs:
            class_name = class_dir.name
            class_id = self.class_mapping[class_name]
            
            # 获取该类别的所有图像
            image_files = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.jpeg")) + list(class_dir.glob("*.png"))
            
            for img_file in image_files:
                all_image_paths.append(str(img_file))
                all_labels.append(class_id)
                
        print(f"📊 总共处理 {len(all_image_paths)} 张图像")
        
        # 划分训练集、验证集、测试集 (7:2:1)
        train_ratio = self.config.get('train_ratio', 0.7)
        val_ratio = self.config.get('val_ratio', 0.2)
        test_ratio = 1 - train_ratio - val_ratio
        
        # 首先分离训练集和临时集
        train_paths, temp_paths, train_labels, temp_labels = train_test_split(
            all_image_paths, all_labels, 
            train_size=train_ratio, 
            stratify=all_labels, 
            random_state=42
        )
        
        # 再从临时集分离验证集和测试集
        val_paths, test_paths, val_labels, test_labels = train_test_split(
            temp_paths, temp_labels,
            train_size=val_ratio/(val_ratio + test_ratio),
            stratify=temp_labels,
            random_state=42
        )
        
        print(f"📈 数据集划分:")
        print(f"  训练集: {len(train_paths)} 张 ({len(train_paths)/len(all_image_paths)*100:.1f}%)")
        print(f"  验证集: {len(val_paths)} 张 ({len(val_paths)/len(all_image_paths)*100:.1f}%)")
        print(f"  测试集: {len(test_paths)} 张 ({len(test_paths)/len(all_image_paths)*100:.1f}%)")
        
        # 复制图像并创建标签
        def copy_images_and_create_labels(paths, labels, img_dir, label_dir, split_name):
            print(f"🔄 处理{split_name}集...")
            for img_path, label in zip(paths, labels):
                # 复制图像
                img_file = Path(img_path)
                dst_img_path = img_dir / img_file.name
                shutil.copy2(img_path, dst_img_path)
                
                # 创建YOLO格式标签 (对于分类任务，我们创建整图标注)
                label_file = label_dir / f"{img_file.stem}.txt"
                
                # 读取图像尺寸
                img = cv2.imread(img_path)
                h, w = img.shape[:2]
                
                # YOLO格式: class_id center_x center_y width height (归一化)
                # 对于分类任务，我们将整个图像作为一个边界框
                with open(label_file, 'w') as f:
                    f.write(f"{label} 0.5 0.5 1.0 1.0\n")
                    
        copy_images_and_create_labels(train_paths, train_labels, train_img_dir, train_label_dir, "训练")
        copy_images_and_create_labels(val_paths, val_labels, val_img_dir, val_label_dir, "验证")
        copy_images_and_create_labels(test_paths, test_labels, test_img_dir, test_label_dir, "测试")
        
        # 创建类别文件
        with open(yolo_dir / "classes.txt", 'w', encoding='utf-8') as f:
            for class_name in self.class_names:
                f.write(f"{class_name}\n")
                
        # 创建YOLO数据配置文件
        yaml_content = {
            'path': str(yolo_dir.absolute()),
            'train': 'train/images',
            'val': 'val/images',
            'test': 'test/images',
            'nc': len(self.class_names),
            'names': self.class_names
        }
        
        with open(yolo_dir / "dataset.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(yaml_content, f, default_flow_style=False, allow_unicode=True)
            
        self.yolo_dataset_path = yolo_dir / "dataset.yaml"
        print(f"✅ YOLO数据集准备完成: {yolo_dir}")
        
        return yolo_dir
        
    def create_improved_model_config(self):
        """创建改进的YOLO模型配置"""
        print("\n⚙️ 创建改进的模型配置...")
        
        # 基于作物病害检测任务的特点定制配置
        improved_config = {
            # 模型结构优化
            'model': {
                'type': 'YOLOv8',
                'size': self.config.get('model_size', 'n'),  # n, s, m, l, x
                'pretrained': True,
                'freeze_backbone': False,  # 是否冻结backbone
            },
            
            # 训练超参数优化
            'training': {
                'epochs': self.config.get('epochs', 100),
                'batch_size': self.config.get('batch_size', 16),
                'imgsz': self.config.get('img_size', 640),
                'optimizer': 'AdamW',  # 使用AdamW优化器
                'lr0': 0.001,  # 初始学习率
                'lrf': 0.01,   # 最终学习率因子
                'momentum': 0.937,
                'weight_decay': 0.0005,
                'warmup_epochs': 3,
                'warmup_momentum': 0.8,
                'warmup_bias_lr': 0.1,
            },
            
            # 数据增强策略
            'augmentation': {
                'hsv_h': 0.015,      # 色调增强
                'hsv_s': 0.7,        # 饱和度增强
                'hsv_v': 0.4,        # 亮度增强
                'degrees': 10.0,     # 旋转角度
                'translate': 0.1,    # 平移
                'scale': 0.5,        # 缩放
                'shear': 0.0,        # 剪切
                'perspective': 0.0,  # 透视变换
                'flipud': 0.5,       # 垂直翻转
                'fliplr': 0.5,       # 水平翻转
                'mosaic': 1.0,       # 马赛克增强
                'mixup': 0.1,        # mixup增强
                'copy_paste': 0.1,   # 复制粘贴增强
            },
            
            # 损失函数优化
            'loss': {
                'cls': 0.5,          # 分类损失权重
                'box': 7.5,          # 边界框损失权重
                'dfl': 1.5,          # DFL损失权重
                'focal_loss_gamma': 1.5,  # Focal loss gamma
                'label_smoothing': 0.1,   # 标签平滑
            }
        }
        
        # 保存配置
        config_file = self.output_dir / "improved_model_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(improved_config, f, default_flow_style=False, allow_unicode=True)
            
        print(f"💾 改进配置已保存: {config_file}")
        return improved_config
        
    def train_model(self):
        """训练YOLO模型"""
        print("\n🚀 开始训练YOLO模型...")
        
        # 创建改进配置
        improved_config = self.create_improved_model_config()
        
        # 选择模型大小
        model_size = improved_config['model']['size']
        model_name = f"yolov8{model_size}.pt"
        
        print(f"📦 使用模型: {model_name}")
        
        # 初始化YOLO模型
        model = YOLO(model_name)
        
        # 训练参数
        train_params = {
            'data': str(self.yolo_dataset_path),
            'epochs': improved_config['training']['epochs'],
            'batch': improved_config['training']['batch_size'],
            'imgsz': improved_config['training']['imgsz'],
            'optimizer': improved_config['training']['optimizer'],
            'lr0': improved_config['training']['lr0'],
            'lrf': improved_config['training']['lrf'],
            'momentum': improved_config['training']['momentum'],
            'weight_decay': improved_config['training']['weight_decay'],
            'warmup_epochs': improved_config['training']['warmup_epochs'],
            'warmup_momentum': improved_config['training']['warmup_momentum'],
            'warmup_bias_lr': improved_config['training']['warmup_bias_lr'],
            'project': str(self.output_dir),
            'name': f'crop_disease_yolo_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'save': True,
            'save_period': 10,  # 每10个epoch保存一次
            'cache': False,     # 不缓存图像到内存
            'device': 'cuda' if torch.cuda.is_available() else 'cpu',
            'workers': 8,
            'verbose': True,
            'seed': 42,
            'deterministic': True,
        }
        
        # 应用数据增强参数
        for key, value in improved_config['augmentation'].items():
            train_params[key] = value
            
        # 应用损失函数参数
        for key, value in improved_config['loss'].items():
            train_params[key] = value
            
        print("🔧 训练参数:")
        for key, value in train_params.items():
            print(f"  {key}: {value}")
            
        # 开始训练
        print(f"\n🎯 开始训练...")
        results = model.train(**train_params)
        
        # 保存训练结果
        self.trained_model = model
        self.training_results = results
        
        print("✅ 模型训练完成!")
        return results
        
    def evaluate_model(self):
        """评估模型性能"""
        print("\n📊 评估模型性能...")
        
        if not hasattr(self, 'trained_model'):
            print("❌ 没有训练好的模型，请先运行训练")
            return None
            
        # 在验证集上评估
        val_results = self.trained_model.val()
        
        # 在测试集上进行推理并评估
        test_img_dir = self.output_dir / "yolo_dataset" / "test" / "images"
        test_images = list(test_img_dir.glob("*.jpg")) + list(test_img_dir.glob("*.png"))
        
        if test_images:
            print(f"🧪 在 {len(test_images)} 张测试图像上评估...")
            
            # 批量预测
            results = self.trained_model.predict(source=str(test_img_dir), save=False, verbose=False)
            
            # 收集预测结果
            predictions = []
            true_labels = []
            
            for i, result in enumerate(results):
                # 获取图像文件名
                img_path = test_images[i]
                
                # 读取真实标签
                label_file = test_img_dir.parent / "labels" / f"{img_path.stem}.txt"
                if label_file.exists():
                    with open(label_file, 'r') as f:
                        true_class = int(f.readline().strip().split()[0])
                        true_labels.append(true_class)
                        
                    # 获取预测结果
                    if len(result.boxes) > 0:
                        pred_class = int(result.boxes.cls[0].cpu())
                        predictions.append(pred_class)
                    else:
                        predictions.append(-1)  # 未检测到
                        
            # 计算性能指标
            if predictions and true_labels:
                self.calculate_metrics(true_labels, predictions)
                
        return val_results
        
    def calculate_metrics(self, true_labels, predictions):
        """计算详细的性能指标"""
        print("\n📈 计算性能指标...")
        
        # 过滤掉未检测到的样本
        valid_indices = [i for i, pred in enumerate(predictions) if pred != -1]
        filtered_true = [true_labels[i] for i in valid_indices]
        filtered_pred = [predictions[i] for i in valid_indices]
        
        if not filtered_true:
            print("❌ 没有有效的预测结果")
            return
            
        # 计算分类报告
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
        
        accuracy = accuracy_score(filtered_true, filtered_pred)
        precision, recall, f1, support = precision_recall_fscore_support(filtered_true, filtered_pred, average='weighted')
        
        print(f"🎯 整体性能指标:")
        print(f"  准确率 (Accuracy): {accuracy:.4f}")
        print(f"  精确率 (Precision): {precision:.4f}")
        print(f"  召回率 (Recall): {recall:.4f}")
        print(f"  F1分数: {f1:.4f}")
        print(f"  检测率: {len(filtered_true)}/{len(true_labels)} ({len(filtered_true)/len(true_labels)*100:.1f}%)")
        
        # 详细分类报告
        class_names_filtered = [self.class_names[i] for i in range(len(self.class_names)) if i in set(filtered_true + filtered_pred)]
        report = classification_report(filtered_true, filtered_pred, target_names=class_names_filtered)
        
        # 保存报告
        report_file = self.output_dir / "performance_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 作物病害检测模型性能报告\n\n")
            f.write(f"## 整体性能\n")
            f.write(f"- 准确率: {accuracy:.4f}\n")
            f.write(f"- 精确率: {precision:.4f}\n")
            f.write(f"- 召回率: {recall:.4f}\n")
            f.write(f"- F1分数: {f1:.4f}\n")
            f.write(f"- 检测率: {len(filtered_true)}/{len(true_labels)} ({len(filtered_true)/len(true_labels)*100:.1f}%)\n\n")
            f.write(f"## 详细分类报告\n")
            f.write(report)
            
        print(f"📄 性能报告已保存: {report_file}")
        
        # 绘制混淆矩阵
        self.plot_confusion_matrix(filtered_true, filtered_pred)
        
    def plot_confusion_matrix(self, true_labels, predictions):
        """绘制混淆矩阵"""
        from sklearn.metrics import confusion_matrix
        
        cm = confusion_matrix(true_labels, predictions)
        
        plt.figure(figsize=(12, 10))
        
        # 只显示出现在测试集中的类别
        unique_labels = sorted(set(true_labels + predictions))
        class_names_subset = [self.class_names[i] for i in unique_labels]
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=class_names_subset,
                   yticklabels=class_names_subset)
        plt.title('混淆矩阵')
        plt.xlabel('预测类别')
        plt.ylabel('真实类别')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        cm_file = self.output_dir / "confusion_matrix.png"
        plt.savefig(cm_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 混淆矩阵已保存: {cm_file}")
        
    def save_final_model(self):
        """保存最终模型"""
        print("\n💾 保存最终模型...")
        
        if not hasattr(self, 'trained_model'):
            print("❌ 没有训练好的模型")
            return
            
        # 保存模型权重
        model_file = self.output_dir / "best_crop_disease_model.pt"
        self.trained_model.export(format='onnx')  # 导出ONNX格式
        
        # 复制最佳权重
        runs_dir = self.output_dir / "runs" / "detect"
        if runs_dir.exists():
            latest_run = max(runs_dir.glob("crop_disease_yolo_*"), key=os.path.getctime, default=None)
            if latest_run and (latest_run / "weights" / "best.pt").exists():
                shutil.copy2(latest_run / "weights" / "best.pt", model_file)
                print(f"✅ 最佳模型已保存: {model_file}")
                
        # 保存模型信息
        model_info = {
            'model_type': 'YOLOv8',
            'num_classes': len(self.class_names),
            'class_names': self.class_names,
            'image_size': self.config.get('img_size', 640),
            'training_date': datetime.now().isoformat(),
            'config': self.config
        }
        
        info_file = self.output_dir / "model_info.yaml"
        with open(info_file, 'w', encoding='utf-8') as f:
            yaml.dump(model_info, f, default_flow_style=False, allow_unicode=True)
            
        print(f"📋 模型信息已保存: {info_file}")


def main():
    """主训练流程"""
    parser = argparse.ArgumentParser(description='YOLO作物病害检测模型训练')
    parser.add_argument('--dataset', type=str, 
                       default=r"F:\photos\Data for Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network\Plant_leaf_diseases_dataset_with_augmentation\Plant_leave_diseases_dataset_with_augmentation",
                       help='数据集路径')
    parser.add_argument('--output', type=str, default='model-training/outputs', help='输出目录')
    parser.add_argument('--epochs', type=int, default=100, help='训练轮数')
    parser.add_argument('--batch-size', type=int, default=16, help='批次大小')
    parser.add_argument('--img-size', type=int, default=640, help='图像尺寸')
    parser.add_argument('--model-size', type=str, default='n', choices=['n', 's', 'm', 'l', 'x'], help='模型大小')
    
    args = parser.parse_args()
    
    # 配置参数
    config = {
        'dataset_path': args.dataset,
        'output_dir': args.output,
        'epochs': args.epochs,
        'batch_size': args.batch_size,
        'img_size': args.img_size,
        'model_size': args.model_size,
        'train_ratio': 0.7,
        'val_ratio': 0.2,
        'random_seed': 42
    }
    
    print("🌱 YOLO作物病害检测模型训练")
    print("=" * 50)
    
    # 创建训练器
    trainer = CropDiseaseYOLOTrainer(config)
    
    try:
        # 1. 准备数据集
        trainer.prepare_dataset()
        
        # 2. 训练模型
        trainer.train_model()
        
        # 3. 评估模型
        trainer.evaluate_model()
        
        # 4. 保存最终模型
        trainer.save_final_model()
        
        print("\n🎉 训练流程完成!")
        print(f"📁 查看结果: {trainer.output_dir}")
        
    except Exception as e:
        print(f"❌ 训练过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
