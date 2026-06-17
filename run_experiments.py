# run_experiments.py
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joblib
import os

from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

from src.data_loader import load_and_clean_data
from src.feature_engineering import prepare_features

# ========== 1. 加载数据 ==========
print("="*60)
print("第 4 步：多算法实验")
print("="*60)

print("\n正在加载数据...")
train_path = 'data/Dry_Bean_Dataset_Dirty_train.xlsx'
val_path   = 'data/Dry_Bean_Dataset_Dirty_val.xlsx'
test_path  = 'data/Dry_Bean_Dataset_Dirty_test.xlsx'

train_df = load_and_clean_data(train_path)
val_df   = load_and_clean_data(val_path)
test_df  = load_and_clean_data(test_path)

# 合并 train + val 作为最终训练集
train_df = pd.concat([train_df, val_df], ignore_index=True)

X_train, y_train, X_val, y_val, X_test, y_test, scaler = prepare_features(
    train_df, val_df, test_df
)

# 合并训练集和验证集
X_train_full = np.vstack([X_train, X_val])
y_train_full = np.concatenate([y_train, y_val])

# 将标签编码为数值（XGBoost 要求）
label_encoder = LabelEncoder()
y_train_full = label_encoder.fit_transform(y_train_full)
y_test = label_encoder.transform(y_test)

print(f"\n最终训练集: {X_train_full.shape[0]} 样本")
print(f"测试集: {X_test.shape[0]} 样本")
print(f"类别映射: {dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))}")

# ========== 2. 定义算法 ==========
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
        use_label_encoder=False
    )
}

results = []

# ========== 3. 训练 & 评估 ==========
print("\n" + "="*60)
print("开始训练和评估...")
print("="*60)

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
    
    results.append({
        'Model': name,
        'Train Acc': train_acc,
        'Test Acc': test_acc,
        'Overfit Gap': overfit_gap,
        'Train Time (s)': train_time,
        'Infer Time (ms/1000)': infer_time
    })

# ========== 4. 打印结果表格 ==========
print("\n" + "="*60)
print("实验结果汇总")
print("="*60)
results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

# ========== 5. 鲁棒性测试 ==========
print("\n" + "="*60)
print("鲁棒性测试（高斯噪声）")
print("="*60)

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

# ========== 6. 绘制 XGBoost Loss 曲线 ==========
print("\n" + "="*60)
print("绘制 XGBoost 训练曲线...")
print("="*60)

# 重新训练 XGBoost 并记录 eval 曲线（使用编码后的 y）
xgb = XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=6,
    random_state=42,
    eval_metric='mlogloss',
    use_label_encoder=False
)

# 注意 y_train 和 y_val 也需要编码（但我们在上面只编码了 y_train_full 和 y_test）
# 这里需要将 y_train 和 y_val 也编码
y_train_encoded = label_encoder.transform(y_train)
y_val_encoded = label_encoder.transform(y_val)

xgb.fit(
    X_train, y_train_encoded,
    eval_set=[(X_train, y_train_encoded), (X_val, y_val_encoded)],
    verbose=False
)

evals_result = xgb.evals_result()
train_loss = evals_result['validation_0']['mlogloss']
val_loss = evals_result['validation_1']['mlogloss']

plt.figure(figsize=(8, 5))
plt.plot(train_loss, label='Train Loss', linewidth=2)
plt.plot(val_loss, label='Validation Loss', linewidth=2)
plt.xlabel('Epoch')
plt.ylabel('Log Loss')
plt.title('XGBoost 训练曲线')
plt.legend()
plt.grid(True, alpha=0.3)
os.makedirs('results/figures', exist_ok=True)
plt.savefig('results/figures/xgb_loss_curve.png', dpi=150, bbox_inches='tight')
print("✅ Loss 曲线已保存到: results/figures/xgb_loss_curve.png")

# ========== 7. 绘制鲁棒性对比图 ==========
plt.figure(figsize=(8, 5))
for name in models.keys():
    plt.plot(noise_levels, robust_results[name], marker='o', label=name, linewidth=2)
plt.xlabel('噪声强度')
plt.ylabel('测试集精度')
plt.title('不同算法的鲁棒性对比')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('results/figures/robustness_comparison.png', dpi=150, bbox_inches='tight')
print("✅ 鲁棒性对比图已保存到: results/figures/robustness_comparison.png")

# ========== 8. 保存结果 ==========
results_df.to_csv('results/metrics.csv', index=False)
print("\n✅ 完整结果已保存到: results/metrics.csv")

print("\n" + "="*60)
print("🎉 多算法实验全部完成！")
print("="*60)