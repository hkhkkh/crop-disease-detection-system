#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据集分析与处理脚本
用于分析植物病害数据集的结构和统计信息
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import Counter
import cv2
import numpy as np
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

class DatasetAnalyzer:
    def __init__(self, dataset_path):
        """初始化数据集分析器"""
        self.dataset_path = Path(dataset_path)
        self.class_info = {}
        self.total_images = 0
        
    def analyze_dataset_structure(self):
        """分析数据集结构"""
        print("🔍 开始分析数据集结构...")
        
        if not self.dataset_path.exists():
            print(f"❌ 数据集路径不存在: {self.dataset_path}")
            return False
            
        # 获取所有类别目录
        class_dirs = [d for d in self.dataset_path.iterdir() if d.is_dir()]
        
        print(f"📊 发现 {len(class_dirs)} 个类别:")
        
        for class_dir in sorted(class_dirs):
            # 统计每个类别的图片数量
            image_files = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.jpeg")) + list(class_dir.glob("*.png"))
            image_count = len(image_files)
            
            # 解析类别信息
            class_name = class_dir.name
            if "___" in class_name:
                crop_type, disease_name = class_name.split("___", 1)
            else:
                crop_type = "Unknown"
                disease_name = class_name
                
            self.class_info[class_name] = {
                'crop_type': crop_type,
                'disease_name': disease_name,
                'image_count': image_count,
                'path': str(class_dir)
            }
            
            self.total_images += image_count
            print(f"  📁 {class_name}: {image_count} 张图片")
            
        print(f"\n📈 总计: {self.total_images} 张图片")
        return True
        
    def generate_statistics(self):
        """生成数据集统计信息"""
        print("\n📊 生成统计信息...")
        
        # 按作物类型统计
        crop_stats = {}
        disease_stats = {}
        
        for class_name, info in self.class_info.items():
            crop_type = info['crop_type']
            disease_name = info['disease_name']
            count = info['image_count']
            
            # 作物类型统计
            if crop_type not in crop_stats:
                crop_stats[crop_type] = {'classes': 0, 'images': 0}
            crop_stats[crop_type]['classes'] += 1
            crop_stats[crop_type]['images'] += count
            
            # 病害类型统计
            if disease_name not in disease_stats:
                disease_stats[disease_name] = 0
            disease_stats[disease_name] += count
            
        # 保存统计结果
        stats = {
            'total_classes': len(self.class_info),
            'total_images': self.total_images,
            'crop_stats': crop_stats,
            'disease_stats': disease_stats,
            'class_info': self.class_info
        }
        
        # 保存到JSON文件
        stats_file = Path("model-training/dataset_statistics.json")
        stats_file.parent.mkdir(exist_ok=True)
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
            
        print(f"📄 统计信息已保存到: {stats_file}")
        return stats
        
    def visualize_statistics(self, stats):
        """可视化数据集统计信息"""
        print("\n📈 生成可视化图表...")
        
        # 创建输出目录
        output_dir = Path("model-training/analysis_plots")
        output_dir.mkdir(exist_ok=True)
        
        # 1. 作物类型分布
        plt.figure(figsize=(12, 8))
        crop_names = list(stats['crop_stats'].keys())
        crop_counts = [stats['crop_stats'][crop]['images'] for crop in crop_names]
        
        plt.subplot(2, 2, 1)
        plt.pie(crop_counts, labels=crop_names, autopct='%1.1f%%', startangle=90)
        plt.title('作物类型分布')
        
        # 2. 每个类别的图片数量
        plt.subplot(2, 2, 2)
        class_names = list(self.class_info.keys())
        class_counts = [self.class_info[cls]['image_count'] for cls in class_names]
        
        plt.bar(range(len(class_names)), class_counts)
        plt.title('各类别图片数量')
        plt.xlabel('类别')
        plt.ylabel('图片数量')
        plt.xticks(range(len(class_names)), class_names, rotation=90, fontsize=8)
        
        # 3. 健康vs病害分布
        plt.subplot(2, 2, 3)
        healthy_count = sum([info['image_count'] for name, info in self.class_info.items() if 'healthy' in name.lower()])
        diseased_count = self.total_images - healthy_count
        
        plt.pie([healthy_count, diseased_count], labels=['健康', '病害'], autopct='%1.1f%%', startangle=90)
        plt.title('健康 vs 病害分布')
        
        # 4. 数据平衡性分析
        plt.subplot(2, 2, 4)
        plt.hist(class_counts, bins=20, edgecolor='black')
        plt.title('类别数据分布')
        plt.xlabel('图片数量')
        plt.ylabel('类别数')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'dataset_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 可视化图表已保存到: {output_dir}")
        
    def sample_images_analysis(self):
        """分析样本图像的基本信息"""
        print("\n🖼️ 分析样本图像...")
        
        image_stats = {
            'widths': [],
            'heights': [],
            'channels': [],
            'formats': []
        }
        
        # 随机采样一些图像进行分析
        sample_count = 0
        max_samples = 100  # 限制采样数量以节省时间
        
        for class_name, info in self.class_info.items():
            if sample_count >= max_samples:
                break
                
            class_path = Path(info['path'])
            image_files = list(class_path.glob("*.jpg")) + list(class_path.glob("*.jpeg")) + list(class_path.glob("*.png"))
            
            # 从每个类别采样2-3张图片
            sample_size = min(3, len(image_files))
            sampled_files = np.random.choice(image_files, sample_size, replace=False)
            
            for img_file in sampled_files:
                if sample_count >= max_samples:
                    break
                    
                try:
                    img = cv2.imread(str(img_file))
                    if img is not None:
                        h, w, c = img.shape
                        image_stats['heights'].append(h)
                        image_stats['widths'].append(w)
                        image_stats['channels'].append(c)
                        image_stats['formats'].append(img_file.suffix.lower())
                        sample_count += 1
                except Exception as e:
                    print(f"⚠️ 无法读取图像 {img_file}: {e}")
                    
        # 统计图像信息
        if image_stats['widths']:
            print(f"📏 采样图像统计 (基于 {sample_count} 张图片):")
            print(f"  宽度: {np.min(image_stats['widths'])} - {np.max(image_stats['widths'])} (平均: {np.mean(image_stats['widths']):.1f})")
            print(f"  高度: {np.min(image_stats['heights'])} - {np.max(image_stats['heights'])} (平均: {np.mean(image_stats['heights']):.1f})")
            print(f"  通道数: {Counter(image_stats['channels'])}")
            print(f"  格式: {Counter(image_stats['formats'])}")
            
        return image_stats
        
    def create_yolo_format_structure(self):
        """创建YOLO格式的数据集结构"""
        print("\n🎯 创建YOLO训练数据结构...")
        
        # 创建YOLO格式目录
        yolo_dir = Path("model-training/yolo_dataset")
        
        # 创建目录结构
        dirs_to_create = [
            yolo_dir / "train" / "images",
            yolo_dir / "train" / "labels", 
            yolo_dir / "val" / "images",
            yolo_dir / "val" / "labels",
            yolo_dir / "test" / "images",
            yolo_dir / "test" / "labels"
        ]
        
        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        # 创建类别映射文件
        class_names = sorted(self.class_info.keys())
        class_mapping = {name: idx for idx, name in enumerate(class_names)}
        
        # 保存类别映射
        with open(yolo_dir / "classes.txt", 'w', encoding='utf-8') as f:
            for class_name in class_names:
                f.write(f"{class_name}\n")
                
        # 创建YOLO数据配置文件
        yaml_content = f"""# 植物病害检测数据集配置
path: {yolo_dir.absolute()}
train: train/images
val: val/images
test: test/images

# 类别数量
nc: {len(class_names)}

# 类别名称
names: {class_names}
"""
        
        with open(yolo_dir / "dataset.yaml", 'w', encoding='utf-8') as f:
            f.write(yaml_content)
            
        print(f"📂 YOLO数据集结构已创建: {yolo_dir}")
        print(f"📋 类别映射已保存: {yolo_dir / 'classes.txt'}")
        print(f"⚙️ YOLO配置已保存: {yolo_dir / 'dataset.yaml'}")
        
        return yolo_dir, class_mapping
        
    def generate_report(self, stats):
        """生成数据集分析报告"""
        print("\n📋 生成分析报告...")
        
        report = f"""# 植物病害数据集分析报告

## 📊 数据集概览
- **总类别数**: {stats['total_classes']} 个
- **总图片数**: {stats['total_images']:,} 张
- **数据集路径**: {self.dataset_path}

## 🌱 作物类型分布
"""
        
        for crop, info in sorted(stats['crop_stats'].items()):
            report += f"- **{crop}**: {info['classes']} 个类别, {info['images']:,} 张图片\n"
            
        report += f"""
## 🦠 病害类型统计
共发现 {len(stats['disease_stats'])} 种不同的病害类型：
"""
        
        # 显示前10个最常见的病害
        top_diseases = sorted(stats['disease_stats'].items(), key=lambda x: x[1], reverse=True)[:10]
        for disease, count in top_diseases:
            report += f"- **{disease}**: {count:,} 张图片\n"
            
        report += f"""
## 📈 数据质量评估
### 数据平衡性
- 最多图片的类别: {max(stats['class_info'].values(), key=lambda x: x['image_count'])['image_count']:,} 张
- 最少图片的类别: {min(stats['class_info'].values(), key=lambda x: x['image_count'])['image_count']:,} 张
- 平均每类图片数: {stats['total_images'] / stats['total_classes']:.0f} 张

### 健康样本比例
- 健康样本: {sum([info['image_count'] for name, info in stats['class_info'].items() if 'healthy' in name.lower()]):,} 张
- 病害样本: {stats['total_images'] - sum([info['image_count'] for name, info in stats['class_info'].items() if 'healthy' in name.lower()]):,} 张

## 🎯 YOLO训练建议
1. **数据预处理**: 建议将图像resize到640x640像素
2. **数据增强**: 可使用旋转、翻转、亮度调整等技术
3. **训练策略**: 建议使用7:2:1的训练/验证/测试划分
4. **模型选择**: 推荐使用YOLOv8n或YOLOv8s作为baseline

## 📝 注意事项
- 数据集包含增强后的数据，训练时需注意避免过拟合
- 建议对图像质量进行人工抽查
- 可考虑使用迁移学习加速训练过程
"""
        
        # 保存报告
        report_file = Path("model-training/dataset_analysis_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
            
        print(f"📄 分析报告已保存到: {report_file}")


def main():
    """主函数"""
    print("🌱 植物病害数据集分析工具")
    print("=" * 50)
    
    # 数据集路径
    dataset_path = r"F:\photos\Data for Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network\Plant_leaf_diseases_dataset_with_augmentation\Plant_leave_diseases_dataset_with_augmentation"
    
    # 创建分析器
    analyzer = DatasetAnalyzer(dataset_path)
    
    # 分析数据集结构
    if not analyzer.analyze_dataset_structure():
        return
        
    # 生成统计信息
    stats = analyzer.generate_statistics()
    
    # 可视化统计信息
    analyzer.visualize_statistics(stats)
    
    # 分析样本图像
    analyzer.sample_images_analysis()
    
    # 创建YOLO格式结构
    analyzer.create_yolo_format_structure()
    
    # 生成分析报告
    analyzer.generate_report(stats)
    
    print("\n✅ 数据集分析完成!")
    print("📁 查看生成的文件:")
    print("  - model-training/dataset_statistics.json")
    print("  - model-training/analysis_plots/dataset_analysis.png")
    print("  - model-training/dataset_analysis_report.md")
    print("  - model-training/yolo_dataset/")


if __name__ == "__main__":
    main()
