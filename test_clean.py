from src.data_loader import load_and_clean_data
import pandas as pd
train_path = 'data/Dry_Bean_Dataset_Dirty_train.xlsx'
val_path   = 'data/Dry_Bean_Dataset_Dirty_val.xlsx'
test_path  = 'data/Dry_Bean_Dataset_Dirty_test.xlsx'

print("="*60)
print("清洗前 vs 清洗后对比")
print("="*60)

for name, path in [("训练集", train_path), ("验证集", val_path), ("测试集", test_path)]:
    # 先读原始数据看看形状
    df_raw = pd.read_excel(path)
    print(f"\n【{name}】")
    print(f"  原始: {len(df_raw)} 行")
    
    # 清洗后
    df_clean = load_and_clean_data(path)
    print(f"  清洗后: {len(df_clean)} 行")
    print(f"  删除的行数: {len(df_raw) - len(df_clean)}")
    
    # 检查 Class 列是否还有脏数据
    unique_classes = df_clean['Class'].unique()
    print(f"  清洗后 Class 唯一值: {sorted(unique_classes)}")
    
    # 检查是否还有缺失值
    missing = df_clean.isnull().sum()
    if missing.sum() > 0:
        print(f"  ⚠️ 仍有缺失值: {missing[missing > 0].to_dict()}")
    else:
        print(f"  ✅ 无缺失值")
    
    # 检查是否还有异常值
    area_min = df_clean['Area'].min()
    area_max = df_clean['Area'].max()
    ml_min = df_clean['MajorAxisLength'].min()
    ml_max = df_clean['MajorAxisLength'].max()
    print(f"  Area: [{area_min:.2f}, {area_max:.2f}]")
    print(f"  MajorAxisLength: [{ml_min:.2f}, {ml_max:.2f}]")