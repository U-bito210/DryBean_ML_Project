

<a id="clean"></a>
## 🧹 数据处理

### 数据清洗策略

| 处理步骤 | 方法 | 说明 |
|---------|------|------|
| **类名标准化** | 建立映射字典统一类别名称 | 纠正大小写、拼写错误、数字替字母等 20+ 种变体 |
| **缺失值填充** | 中位数填充 | Perimeter 和 Solidity 列存在缺失，选择中位数对离群值更稳健 |
| **异常值剔除** | 物理阈值过滤 | Area > 0，MajorAxisLength < 1000 |
| **强制数值转换** | pd.to_numeric | 处理 "cm" 后缀等非数值内容 |
| **特征标准化** | StandardScaler | 均值 0，方差 1 |

### 清洗效果

| 数据集 | 原始行数 | 清洗后行数 | 删除行数 | 唯一类别数 |
|--------|---------|-----------|---------|-----------|
| 训练集 | 9527 | 9508 | 19 | 7 |
| 验证集 | 1347 | 1336 | 11 | 7 |
| 测试集 | 2737 | 2712 | 25 | 7 |

全部清洗后，三类数据的 Class 列均只包含 7 个标准类别，无缺失值，无异常值。


<a id="algo"></a>
## 🤖 算法实现

本实验实现 **5 种多分类算法**：

| 算法 | 类型 | 核心特点 |
|------|------|---------|
| Random Forest | 集成学习（Bagging） | 多棵决策树投票，抗过拟合能力强 |
| SVM | 传统机器学习 | RBF 核函数，最大化类别间隔 |
| XGBoost | 梯度提升（Boosting） | 二阶泰勒展开，正则化控制，缺失值自动处理 |
| LightGBM | 梯度提升（Boosting） | 直方图训练，Leaf-wise 生长，训练速度快 |
| MLP | 神经网络 | 双隐藏层（128+64），ReLU + Adam |

> 其中 XGBoost 和 LightGBM 为自行查阅资料实现的算法。


<a id="results"></a>
## 📈 实验结果

### 精度对比表

| 模型 | 训练集精度 | 测试集精度 | 过拟合差距 | 训练耗时(s) | 推理速度(ms/1000条) |
|------|-----------|-----------|-----------|------------|-------------------|
| **XGBoost** | 97.42% | **93.03%** | 4.39% | 0.61 | **2.00** |
| SVM | 93.13% | 92.96% | **0.17%** | **0.31** | 119.54 |
| LightGBM | 99.38% | 92.70% | 6.69% | 2.15 | 4.80 |
| MLP | 93.13% | 92.59% | 0.54% | 2.56 | 2.99 |
| Random Forest | 100.00% | 92.00% | 8.00% | 0.30 | 26.79 |

### 关键结论

- 🏆 **XGBoost**：测试精度最高（93.03%），推理速度最快（2ms/1000条），综合表现最优
- 🛡️ **SVM**：泛化能力最强（过拟合差距仅 0.17%），鲁棒性最好
- ⚡ **LightGBM**：训练速度快，但过拟合较明显（6.69%）
- 📊 **MLP**：表现稳健（92.59%），过拟合很小（0.54%）
- 🌲 **Random Forest**：训练集 100% 过拟合明显，但测试精度仍达 92%

### 特征重要性（XGBoost）

![特征重要性](results/figures/feature_importance.png)

**ShapeFactor3**（31.68%）和 **ConvexArea**（21.71%）是最关键的两个特征，合计贡献超过 50% 的分类信息。Eccentricity 和 EquivDiameter 的重要性均为 0，表明这两个特征在分类过程中未提供有效信息，后续可考虑剔除。

### 鲁棒性对比

![鲁棒性对比](results/figures/robustness_comparison.png)

SVM 在所有噪声强度下均表现最稳健，20% 噪声下仍保持 **91.96%** 精度。树模型在 20% 噪声下均出现约 3-4% 的精度下降。

### Loss 曲线对比

![Loss对比](results/figures/loss_curve_comparison.png)

XGBoost 和 LightGBM 同为梯度提升树模型，迭代单位一致（均为单轮新增一棵决策树）。LightGBM 在训练初期损失下降更快，收敛速度优于 XGBoost；从最终损失值来看，LightGBM 的训练与验证损失均低于 XGBoost。验证集上的损失优劣趋势与测试集精度结果存在小幅差异：验证集上 LightGBM 损失更优，而测试集上 XGBoost 分类准确率（93.03%）略高于 LightGBM（92.70%）。

### 实验图表清单

| 图表名称 | 用途 | 对应章节 |
|---------|------|---------|
| class_distribution.png | 类别分布 | 数据分析 |
| feature_correlation.png | 特征相关性热图 | 数据分析 |
| xgb_loss_curve.png | XGBoost 训练曲线 | Loss 分析 |
| lgb_loss_curve.png | LightGBM 训练曲线 | Loss 分析 |
| mlp_loss_curve.png | MLP 训练曲线 | Loss 分析 |
| loss_curve_comparison.png | XGB vs LGB 对比 | Loss 分析 |
| robustness_comparison.png | 鲁棒性对比 | 鲁棒性分析 |
| feature_importance.png | 特征重要性 | 可解释性分析 |
| efficiency_comparison.png | 训练效率对比 | 效率分析 |
| f1_score_heatmap.png | F1-Score 热图 | 细粒度评估 |
| cm_*.png（5张） | 混淆矩阵 | 错误模式分析 |


<a id="usage"></a>
## 🛠️ 运行方式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行完整实验（5种算法 + 所有对比分析）
python run_experiments.py

# 3. 只做数据清洗
python main.py --mode data

# 4. 预测新数据
python main.py --mode predict --input data/sample.xlsx --output predictions.csv

预期输出

运行 python run_experiments.py 后，终端将依次输出：

1.5 种算法的训练集精度、测试集精度、过拟合差距、训练耗时、推理耗时

2.鲁棒性测试结果（4 种噪声强度）

3.特征重要性分析

4.所有图表自动保存至 results/figures/ 目录

<a id="structure"></a>

##📁 项目结构

text
DryBean_ML_Project/
├── data/                     # 原始数据（三个 Excel 文件）
├── src/
│   ├── __init__.py
│   ├── data_loader.py        # 数据加载与清洗
│   └── feature_engineering.py # 特征工程（标准化）
├── models/                   # 5 个已训练模型 + scaler.pkl
├── results/
│   ├── metrics.csv           # 精度对比表
│   └── figures/              # 17 张实验图表
├── run_experiments.py        # 完整实验脚本
├── main.py                   # 统一命令行入口
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md