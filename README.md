# DryBean_ML_Project

基于 Dry Bean Dataset 的完整机器学习分类项目，涵盖数据分析、数据清洗、特征工程、5种多分类算法对比实验和系统集成。


## 📊 数据描述

本实验使用 Dry Bean Dataset，包含 7 种干豆类别：BARBUNYA、BOMBAY、CALI、DERMASON、HOROZ、SEKER、SIRA。每个样本由 16 个形态学特征描述，包括面积、周长、长轴、短轴、长宽比、偏心率、圆度、紧凑度等。教师已预先将数据划分为训练集、验证集和测试集。


## 🧹 数据处理

- 缺失值填充：Perimeter 和 Solidity 列使用中位数填充
- 异常值剔除：Area > 0，MajorAxisLength < 1000
- 类名标准化：统一 7 个标准类别，纠正大小写、拼写错误和数字替字母
- 特征标准化：使用 StandardScaler 进行标准化


## 🤖 算法实现

本实验实现了 5 种多分类算法（含 2 种课上未讲算法）：

| 算法 | 类型 | 课上是否讲过 |
|------|------|-------------|
| Random Forest | 集成学习 | 是 |
| SVM | 传统机器学习 | 是 |
| XGBoost | 梯度提升 | 否 |
| LightGBM | 梯度提升 | 否 |
| MLP | 神经网络 | 是 |


## 📈 实验结果（精度表）

| 模型 | 测试集精度 | 过拟合差距 | 推理速度(ms/1000条) |
|------|-----------|-----------|-------------------|
| XGBoost | 93.03% | 4.39% | 2.00 |
| SVM | 92.96% | 0.17% | 119.54 |
| LightGBM | 92.70% | 6.69% | 4.80 |
| MLP | 92.59% | 0.54% | 2.99 |
| Random Forest | 92.00% | 8.00% | 26.79 |

结论：XGBoost 在测试集上取得最高精度（93.03%），推理速度最快（2ms/1000条）；SVM 泛化能力最强（过拟合差距仅 0.17%）。


## 🛠️ 运行方式

```bash
# 安装依赖
pip install -r requirements.txt

# 运行完整实验
python run_experiments.py

# 数据清洗
python main.py --mode data

##📁 项目结构

DryBean_ML_Project/
├── data/                     # 原始数据（三个Excel文件）
├── src/
│   ├── __init__.py
│   ├── data_loader.py        # 数据加载与清洗
│   └── feature_engineering.py # 特征工程（标准化）
├── models/                   # 5个已训练模型 + scaler.pkl
├── results/
│   ├── metrics.csv           # 精度对比表
│   └── figures/              # 17张实验图表
├── run_experiments.py        # 完整实验脚本
├── main.py                   # 统一命令行入口
├── requirements.txt
├── .gitignore
└── README.md