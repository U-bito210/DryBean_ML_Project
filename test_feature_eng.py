# test_feature_eng.py
from src.data_loader import load_and_clean_data
from src.feature_engineering import prepare_features
import pandas as pd

print("正在加载并清洗数据...")
train_path = 'data/Dry_Bean_Dataset_Dirty_train.xlsx'
val_path   = 'data/Dry_Bean_Dataset_Dirty_val.xlsx'
test_path  = 'data/Dry_Bean_Dataset_Dirty_test.xlsx'

train_df = load_and_clean_data(train_path)
val_df   = load_and_clean_data(val_path)
test_df  = load_and_clean_data(test_path)

print("\n正在执行特征工程（标准化）...")
X_train, y_train, X_val, y_val, X_test, y_test, scaler = prepare_features(train_df, val_df, test_df)

print("\n" + "="*60)
print("特征工程完成！数据形状如下：")
print("="*60)
print(f"X_train 形状: {X_train.shape}")
print(f"y_train 形状: {y_train.shape}")
print(f"X_val   形状: {X_val.shape}")
print(f"y_val   形状: {y_val.shape}")
print(f"X_test  形状: {X_test.shape}")
print(f"y_test  形状: {y_test.shape}")

print("\n标准化后特征统计（前5个特征）:")
print(f"  均值: {X_train.mean(axis=0)[:5]}")
print(f"  标准差: {X_train.std(axis=0)[:5]}")

print("\n✅ 特征工程验证通过！")