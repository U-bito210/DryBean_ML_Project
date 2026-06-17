# src/data_loader.py
import pandas as pd
import numpy as np
import re

# ========== 需要转为数值的特征列 ==========
FEATURE_COLS = [
    'Area', 'Perimeter', 'MajorAxisLength', 'MinorAxisLength',
    'AspectRation', 'Eccentricity', 'ConvexArea', 'EquivDiameter',
    'Extent', 'Solidity', 'roundness', 'Compactness',
    'ShapeFactor1', 'ShapeFactor2', 'ShapeFactor3', 'ShapeFactor4'
]


def clean_class_column(df):
    """
    清洗 Class 列：统一大小写、修正拼写错误、去除空格、纠正数字替字母
    """
    df['Class'] = df['Class'].astype(str).str.strip()
    
    class_mapping = {
        'DERMASON': 'DERMASON', 'dermason': 'DERMASON', 'DERMASON ': 'DERMASON', 'D3RMAS0N': 'DERMASON',
        'SIRA': 'SIRA', 'sira': 'SIRA', 'SIRA ': 'SIRA',
        'SEKER': 'SEKER', 'seker': 'SEKER', 'SEKER ': 'SEKER', 'S3K3R': 'SEKER',
        'HOROZ': 'HOROZ', 'horoz': 'HOROZ', 'HOROZ ': 'HOROZ', 'H0R0Z': 'HOROZ',
        'CALI': 'CALI', 'cali': 'CALI', 'CALI ': 'CALI',
        'BARBUNYA': 'BARBUNYA', 'barbunya': 'BARBUNYA', 'BARBUNYA ': 'BARBUNYA',
        'BOMBAY': 'BOMBAY', 'bombay': 'BOMBAY', 'B0MBAY': 'BOMBAY',
    }
    
    df['Class'] = df['Class'].map(class_mapping).fillna(df['Class'])
    df = df[df['Class'].notna()]
    df = df[df['Class'] != '']
    return df


def force_numeric(df):
    """
    将所有特征列强制转为数值类型，无法转换的变为 NaN
    """
    for col in FEATURE_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def clean_numeric_outliers(df):
    """
    清洗数值列异常值：
    1. Area > 0
    2. MajorAxisLength < 1000
    """
    # 确保两列为数值型
    for col in ['Area', 'MajorAxisLength']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df[df['Area'] > 0]
    df = df[df['MajorAxisLength'] < 1000]
    return df


def fill_missing_values(df):
    """
    对所有特征列用中位数填充缺失值
    """
    for col in FEATURE_COLS:
        if col in df.columns:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
    return df


def load_and_clean_data(file_path):
    """
    完整的加载 + 清洗流程
    """
    df = pd.read_excel(file_path)
    
    # 1. 清洗 Class 列
    df = clean_class_column(df)
    
    # 2. 强制所有特征列为数值型
    df = force_numeric(df)
    
    # 3. 清洗异常值（基于 Area 和 MajorAxisLength）
    df = clean_numeric_outliers(df)
    
    # 4. 填充所有缺失值（用中位数）
    df = fill_missing_values(df)
    
    return df


if __name__ == "__main__":
    # 测试清洗效果
    test_path = 'data/Dry_Bean_Dataset_Dirty_train.xlsx'
    df = load_and_clean_data(test_path)
    print(f"清洗后形状: {df.shape}")
    print(f"列名: {df.columns.tolist()}")
    print(f"缺失值总计: {df.isnull().sum().sum()}")
    print(f"Class 唯一值: {df['Class'].unique()}")
    print(f"各列数据类型:\n{df.dtypes}")
    print("\n前2行:")
    print(df.head(2))