import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# ====== 请按实际文件名修改下面三个路径 ======
train_path = 'data/Dry_Bean_Dataset_Dirty_train.xlsx'
val_path   = 'data/Dry_Bean_Dataset_Dirty_val.xlsx'
test_path  = 'data/Dry_Bean_Dataset_Dirty_test.xlsx'
# ==========================================

def load_and_summary(name, path):
    try:
        df = pd.read_excel(path)
        print(f"\n{'='*60}")
        print(f"【{name}】")
        print(f"形状: {df.shape}")
        print(f"列名: {df.columns.tolist()}")
        print(f"\n前2行:")
        print(df.head(2))
        print(f"\n缺失值统计:")
        print(df.isnull().sum()[df.isnull().sum() > 0])  # 只显示有缺失的列
        print(f"\nClass 列的唯一值（前20个）:")
        print(df['Class'].unique()[:20])
        print(f"\n数值列异常值初探:")
        print(f"  Area 最小值: {df['Area'].min():.2f}, 最大值: {df['Area'].max():.2f}")
        print(f"  MajorAxisLength 最小值: {df['MajorAxisLength'].min():.2f}, 最大值: {df['MajorAxisLength'].max():.2f}")
        return df
    except FileNotFoundError:
        print(f"❌ 文件 {path} 未找到，请检查路径和文件名。")
        return None

# 加载三个数据集
df_train = load_and_summary("训练集", train_path)
df_val   = load_and_summary("验证集", val_path)
df_test  = load_and_summary("测试集", test_path)

# 如果都加载成功，额外看看整体情况
if df_train is not None and df_val is not None and df_test is not None:
    print("\n" + "="*60)
    print("【整体对比】")
    print(f"训练集样本数: {len(df_train)}")
    print(f"验证集样本数: {len(df_val)}")
    print(f"测试集样本数: {len(df_test)}")
    print("\n训练集 Class 分布:")
    print(df_train['Class'].value_counts())
    print("\n验证集 Class 分布:")
    print(df_val['Class'].value_counts())
    print("\n测试集 Class 分布:")
    print(df_test['Class'].value_counts())