# src/feature_engineering.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import os

def prepare_features(train_df, val_df, test_df, target_col='Class'):
    """
    分离特征和目标，并进行标准化（StandardScaler）
    返回: X_train, y_train, X_val, y_val, X_test, y_test, scaler
    """
    # 1. 分离特征和标签
    X_train = train_df.drop(columns=[target_col])
    y_train = train_df[target_col]
    
    X_val = val_df.drop(columns=[target_col])
    y_val = val_df[target_col]
    
    X_test = test_df.drop(columns=[target_col])
    y_test = test_df[target_col]
    
    # 2. 初始化标准化器
    scaler = StandardScaler()
    
    # 3. 在训练集上拟合（只拟合，不转换）
    X_train_scaled = scaler.fit_transform(X_train)
    
    # 4. 在验证集和测试集上转换（用训练集的均值和标准差）
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    # 5. 保存 scaler 供后续预测使用
    os.makedirs('models', exist_ok=True)
    joblib.dump(scaler, 'models/scaler.pkl')
    print("✅ 标准化器已保存到 models/scaler.pkl")
    
    return X_train_scaled, y_train, X_val_scaled, y_val, X_test_scaled, y_test, scaler


def load_scaler():
    """加载保存的标准化器"""
    return joblib.load('models/scaler.pkl')