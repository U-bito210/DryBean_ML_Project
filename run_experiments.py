# run_experiments.py
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from src.data_loader import load_and_clean_data
from src.feature_engineering import prepare_features

# ============================================================
# 1. 加载数据
# ============================================================
print("="*70)
print("第 4 步：多算法实验（5种算法）")
print("="*70)

print("\n正在加载数据...")
train_path = 'data/Dry_Bean_Dataset_Dirty_train.xlsx'
val_path   = 'data/Dry_Bean_Dataset_Dirty_val.xlsx'
test_path  = 'data/Dry_Bean_Dataset_Dirty_test.xlsx'

train_df = load_and_clean_data(train_path)
val_df   = load_and_clean_data(val_path)
test_df  = load_and_clean_data(test_path)

# 合并 train + val
train_df = pd.concat([train_df, val_df], ignore_index=True)

X_train, y_train, X_val, y_val, X_test, y_test, scaler = prepare_features(
    train_df, val_df, test_df
)

X_train_full = np.vstack([X_train, X_val])
y_train_full = np.concatenate([y_train, y_val])

# 标签编码
label_encoder = LabelEncoder()
y_train_full = label_encoder.fit_transform(y_train_full)
y_test = label_encoder.transform(y_test)

print(f"\n最终训练集: {X_train_full.shape[0]} 样本")
print(f"测试集: {X_test.shape[0]} 样本")
print(f"类别映射: {dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))}")
# ============================================================
# 1.1数据分析图表（用于论文第一章）
# ============================================================
print("\n" + "="*70)
print("Generating Data Analysis Charts...")
print("="*70)

# 1. 类别分布图（用合并前的 train_df，包含所有原始数据）
class_counts = train_df['Class'].value_counts()
plt.figure(figsize=(8, 5))
class_counts.plot(kind='bar', color='steelblue')
plt.xlabel('Bean Class')
plt.ylabel('Count')
plt.title('Class Distribution of Dry Bean Dataset')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('results/figures/class_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ 类别分布图已保存: results/figures/class_distribution.png")

# 2. 特征相关性热图（用训练集的特征部分）
feature_cols = [col for col in train_df.columns if col != 'Class']
corr_matrix = train_df[feature_cols].corr()

plt.figure(figsize=(12, 10))
plt.imshow(corr_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
plt.colorbar(label='Correlation')
plt.xticks(range(len(feature_cols)), feature_cols, rotation=90, fontsize=8)
plt.yticks(range(len(feature_cols)), feature_cols, fontsize=8)
plt.title('Feature Correlation Heatmap')
plt.tight_layout()
plt.savefig('results/figures/feature_correlation.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ 特征相关性热图已保存: results/figures/feature_correlation.png")

print("\n" + "="*70)
print("Starting Model Training...")
print("="*70)
# ============================================================
# 2. 定义5种算法
# ============================================================
models = {
    'Random Forest': RandomForestClassifier(
        n_estimators=100, random_state=42, n_jobs=-1
    ),
    'SVM': SVC(
        kernel='rbf', C=1.0, gamma='scale', random_state=42
    ),
    'XGBoost': XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=6,
        random_state=42,
        eval_metric='mlogloss',
        use_label_encoder=False,
        verbosity=0
    ),
    'LightGBM': LGBMClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=6,
        random_state=42,
        verbose=-1
    ),
    'MLP Neural Net': MLPClassifier(
        hidden_layer_sizes=(128, 64),
        activation='relu',
        max_iter=300,
        random_state=42,
        early_stopping=True,
        n_iter_no_change=10,
        verbose=False
    )
}

results = []

# ============================================================
# 3. 训练 & 评估
# ============================================================
print("\n" + "="*70)
print("开始训练和评估...")
print("="*70)

for name, model in models.items():
    print(f"\n>>> 训练 {name} ...")
    
    start_train = time.time()
    model.fit(X_train_full, y_train_full)
    train_time = time.time() - start_train
    
    train_pred = model.predict(X_train_full)
    train_acc = accuracy_score(y_train_full, train_pred)
    
    start_test = time.time()
    test_pred = model.predict(X_test)
    test_time = time.time() - start_test
    test_acc = accuracy_score(y_test, test_pred)
    
    sample = X_test[:1000]
    start_infer = time.time()
    _ = model.predict(sample)
    infer_time = (time.time() - start_infer) * 1000
    
    overfit_gap = train_acc - test_acc
    
    print(f"  训练集精度: {train_acc:.4f}")
    print(f"  测试集精度: {test_acc:.4f}")
    print(f"  过拟合差距: {overfit_gap:.4f}")
    print(f"  训练耗时: {train_time:.2f} 秒")
    print(f"  推理耗时 (1000条): {infer_time:.2f} ms")
    
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, f'models/{name.replace(" ", "_")}.pkl')
    
    # 保存混淆矩阵
    cm = confusion_matrix(y_test, test_pred)
    plt.figure(figsize=(6, 5))
    plt.imshow(cm, cmap='Blues')
    plt.title(f'{name} - Confusion Matrix')
    plt.colorbar()
    plt.xlabel('Predicted')
    plt.ylabel('True')
    os.makedirs('results/figures', exist_ok=True)
    plt.savefig(f'results/figures/cm_{name.replace(" ", "_")}.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  混淆矩阵已保存")
    
    results.append({
        'Model': name,
        'Train Acc': train_acc,
        'Test Acc': test_acc,
        'Overfit Gap': overfit_gap,
        'Train Time (s)': train_time,
        'Infer Time (ms/1000)': infer_time
    })

# ============================================================
# 4. 结果汇总
# ============================================================
print("\n" + "="*70)
print("实验结果汇总")
print("="*70)
results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

# ============================================================
# 5. 鲁棒性测试（高斯噪声）
# ============================================================
print("\n" + "="*70)
print("鲁棒性测试（高斯噪声）")
print("="*70)

noise_levels = [0.01, 0.05, 0.1, 0.2]
robust_results = {name: [] for name in models.keys()}

for name, model in models.items():
    print(f"\n>>> {name}")
    for noise in noise_levels:
        noise_std = noise * np.std(X_test, axis=0)
        X_noisy = X_test + np.random.normal(0, noise_std, X_test.shape)
        acc = accuracy_score(y_test, model.predict(X_noisy))
        robust_results[name].append(acc)
        print(f"  噪声 {noise*100:.0f}%: 精度 {acc:.4f}")

# ============================================================
# 6. Loss 曲线对比（XGBoost + LightGBM + MLP）
# ============================================================
print("\n" + "="*70)
print("绘制训练曲线对比...")
print("="*70)

# 6.1 XGBoost Loss
xgb = XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=6,
    random_state=42,
    eval_metric='mlogloss',
    use_label_encoder=False,
    verbosity=0
)

y_train_encoded = label_encoder.transform(y_train)
y_val_encoded = label_encoder.transform(y_val)

xgb.fit(X_train, y_train_encoded,
        eval_set=[(X_train, y_train_encoded), (X_val, y_val_encoded)],
        verbose=False)

evals = xgb.evals_result()

# 6.2 LightGBM Loss
lgb = LGBMClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=6,
    random_state=42,
    early_stopping_round=10,
    verbose=-1
)

lgb.fit(
    X_train, y_train_encoded,
    eval_set=[(X_train, y_train_encoded), (X_val, y_val_encoded)],
    eval_metric='logloss'
)

lgb_evals = lgb.evals_result_
train_key = list(lgb_evals.keys())[0]
valid_key = list(lgb_evals.keys())[1]
metric_key = list(lgb_evals[train_key].keys())[0]

lgb_train_loss = lgb_evals[train_key][metric_key]
lgb_valid_loss = lgb_evals[valid_key][metric_key]

# 6.3 MLP Loss（重新训练一个专门用于记录loss的MLP）
print("  训练 MLP 用于记录 Loss 曲线...")
mlp_temp = MLPClassifier(
    hidden_layer_sizes=(128, 64),
    activation='relu',
    max_iter=300,
    random_state=42,
    verbose=False
)
mlp_temp.fit(X_train, y_train_encoded)
mlp_loss = mlp_temp.loss_curve_

# 6.4 XGBoost 单独曲线（保留）
plt.figure(figsize=(8, 5))
plt.plot(evals['validation_0']['mlogloss'], label='XGBoost Train', linewidth=2)
plt.plot(evals['validation_1']['mlogloss'], label='XGBoost Validation', linewidth=2)
plt.xlabel('Epoch')
plt.ylabel('Log Loss')
plt.title('XGBoost Training Curve')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('results/figures/xgb_loss_curve.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ XGBoost 单独 Loss 曲线已保存")

# 6.5 LightGBM 单独曲线
plt.figure(figsize=(8, 5))
plt.plot(lgb_train_loss, label='LightGBM Train', linewidth=2)
plt.plot(lgb_valid_loss, label='LightGBM Validation', linewidth=2)
plt.xlabel('Epoch')
plt.ylabel('Log Loss')
plt.title('LightGBM Training Curve')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('results/figures/lgb_loss_curve.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ LightGBM 单独 Loss 曲线已保存")

# 6.6 MLP 单独曲线
plt.figure(figsize=(8, 5))
plt.plot(mlp_loss, label='MLP Train Loss', linewidth=2)
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('MLP Training Curve')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('results/figures/mlp_loss_curve.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ MLP 单独 Loss 曲线已保存")

# 6.7 XGBoost vs LightGBM 对比图（保留）
plt.figure(figsize=(10, 6))
plt.plot(evals['validation_0']['mlogloss'], label='XGBoost Train', linewidth=2, linestyle='-')
plt.plot(evals['validation_1']['mlogloss'], label='XGBoost Validation', linewidth=2, linestyle='--')
plt.plot(lgb_train_loss, label='LightGBM Train', linewidth=2, linestyle='-')
plt.plot(lgb_valid_loss, label='LightGBM Validation', linewidth=2, linestyle='--')
plt.xlabel('Epoch')
plt.ylabel('Log Loss')
plt.title('Loss Curve Comparison: XGBoost vs LightGBM')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('results/figures/loss_curve_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ XGBoost vs LightGBM 对比曲线已保存")

# ============================================================
# 7. 鲁棒性对比图
# ============================================================
plt.figure(figsize=(8, 5))
for name in models.keys():
    plt.plot(noise_levels, robust_results[name], marker='o', label=name, linewidth=2)
plt.xlabel('Noise Level')
plt.ylabel('Test Accuracy')
plt.title('Robustness Comparison')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('results/figures/robustness_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ 鲁棒性对比图已保存")

# ============================================================
# 8. 特征重要性（XGBoost）
# ============================================================
print("\n" + "="*70)
print("特征重要性分析（XGBoost）")
print("="*70)

# 从原始 DataFrame 获取特征名
feature_names = train_df.drop(columns=['Class']).columns.tolist()
importances = xgb.feature_importances_
imp_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
imp_df = imp_df.sort_values('Importance', ascending=False)

print(imp_df.to_string(index=False))

plt.figure(figsize=(8, 5))
plt.barh(imp_df['Feature'][:10], imp_df['Importance'][:10])
plt.xlabel('Importance')
plt.title('XGBoost - Top 10 Feature Importance')
plt.tight_layout()
plt.savefig('results/figures/feature_importance.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ 特征重要性图已保存")
# ============================================================
# 9. 训练时间 vs 测试精度（效率对比）
# ============================================================
print("\n" + "="*70)
print("补充维度1: 训练时间 vs 测试精度")
print("="*70)

plt.figure(figsize=(8, 6))
for i, row in results_df.iterrows():
    plt.scatter(row['Train Time (s)'], row['Test Acc'], s=150, label=row['Model'])
    plt.annotate(row['Model'].replace(' Neural Net', ''), 
                 (row['Train Time (s)'], row['Test Acc']),
                 xytext=(8, 4), textcoords='offset points', fontsize=9)

plt.xlabel('Training Time (seconds)')
plt.ylabel('Test Accuracy')
plt.title('Efficiency Comparison: Training Time vs Test Accuracy')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('results/figures/efficiency_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ 效率对比图已保存: results/figures/efficiency_comparison.png")


# ============================================================
# 10. 按类别的F1-Score对比热图
# ============================================================
print("\n" + "="*70)
print("补充维度2: 各类别 F1-Score 对比")
print("="*70)

from sklearn.metrics import f1_score

class_names = label_encoder.classes_
f1_data = {}

for name, model in models.items():
    pred = model.predict(X_test)
    f1 = f1_score(y_test, pred, average=None)
    f1_data[name] = f1

f1_df = pd.DataFrame(f1_data, index=class_names)

plt.figure(figsize=(10, 6))
plt.imshow(f1_df.T, cmap='Blues', aspect='auto', vmin=0.7, vmax=1.0)
plt.colorbar(label='F1-Score')
plt.xticks(range(len(class_names)), class_names, rotation=45, ha='right')
plt.yticks(range(len(f1_df.columns)), f1_df.columns)
plt.xlabel('Class')
plt.ylabel('Model')
plt.title('F1-Score Comparison by Class and Model')

for i in range(len(f1_df.columns)):
    for j in range(len(class_names)):
        plt.text(j, i, f'{f1_df.iloc[j, i]:.2f}', 
                 ha='center', va='center', color='black' if f1_df.iloc[j, i] > 0.8 else 'white', fontsize=10)

plt.tight_layout()
plt.savefig('results/figures/f1_score_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ F1-Score 热图已保存: results/figures/f1_score_heatmap.png")

print("\n各类别平均 F1-Score (5种算法平均):")
print(f1_df.mean(axis=1).sort_values(ascending=False).to_string())

# ============================================================
# 11. 保存结果
# ============================================================
results_df.to_csv('results/metrics.csv', index=False)
print("\n✅ 完整结果已保存到: results/metrics.csv")

# ============================================================
# 12. 打印分类报告
# ============================================================
print("\n" + "="*70)
print("XGBoost 分类报告（测试集）")
print("="*70)
xgb_pred = models['XGBoost'].predict(X_test)
print(classification_report(y_test, xgb_pred, target_names=label_encoder.classes_))

print("\n" + "="*70)
print("🎉 多算法实验全部完成！(5种算法)")
print("="*70)