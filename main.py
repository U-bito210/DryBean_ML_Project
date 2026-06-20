# main.py - 统一命令行入口
import argparse
import pandas as pd
import joblib
import os
from sklearn.preprocessing import LabelEncoder

from src.data_loader import load_and_clean_data
from src.feature_engineering import prepare_features, load_scaler


def main():
    parser = argparse.ArgumentParser(description='Dry Bean Classification ML Pipeline')
    parser.add_argument('--mode', type=str, default='train',
                        choices=['data', 'train', 'predict'],
                        help='运行模式: data(数据清洗), train(训练), predict(预测)')
    parser.add_argument('--input', type=str, help='预测模式下，输入数据文件路径')
    parser.add_argument('--output', type=str, default='predictions.csv',
                        help='预测结果输出文件')
    args = parser.parse_args()

    # ============================================================
    # 模式1: 数据清洗
    # ============================================================
    if args.mode == 'data':
        print("="*60)
        print("数据清洗模式")
        print("="*60)
        for name, path in [
            ("训练集", "data/Dry_Bean_Dataset_Dirty_train.xlsx"),
            ("验证集", "data/Dry_Bean_Dataset_Dirty_val.xlsx"),
            ("测试集", "data/Dry_Bean_Dataset_Dirty_test.xlsx")
        ]:
            df = load_and_clean_data(path)
            print(f"\n{name}:")
            print(f"  行数: {len(df)}")
            print(f"  类别: {sorted(df['Class'].unique())}")
            print(f"  缺失值: {df.isnull().sum().sum()}")
        print("\n✅ 数据清洗完成")

    # ============================================================
    # 模式2: 训练
    # ============================================================
    elif args.mode == 'train':
        print("="*60)
        print("训练模式")
        print("="*60)
        print("请运行完整实验脚本:")
        print("  python run_experiments.py")
        print("\n该脚本将自动完成:")
        print("  - 数据加载与清洗")
        print("  - 特征工程")
        print("  - 5种算法训练与评估")
        print("  - 生成所有实验图表")

    # ============================================================
    # 模式3: 预测
    # ============================================================
    elif args.mode == 'predict':
        print("="*60)
        print("预测模式")
        print("="*60)

        if args.input is None:
            print("❌ 请指定 --input 文件路径")
            print("示例: python main.py --mode predict --input data/sample.xlsx")
            return

        # 检查模型文件是否存在
        if not os.path.exists('models/XGBoost.pkl'):
            print("❌ 模型未训练，请先运行: python run_experiments.py")
            return

        try:
            # 加载模型和标准化器
            print("加载模型和标准化器...")
            scaler = load_scaler()
            model = joblib.load('models/XGBoost.pkl')

            # 加载并清洗数据
            print(f"加载数据: {args.input}")
            df = load_and_clean_data(args.input)

            # 分离特征
            if 'Class' in df.columns:
                X = df.drop(columns=['Class'])
                y_true = df['Class']
                has_label = True
            else:
                X = df
                has_label = False

            # 标准化
            X_scaled = scaler.transform(X)

            # 预测
            print("预测中...")
            preds = model.predict(X_scaled)

            # 解码标签
            le = LabelEncoder()
            le.fit(['BARBUNYA', 'BOMBAY', 'CALI', 'DERMASON', 'HOROZ', 'SEKER', 'SIRA'])
            pred_labels = le.inverse_transform(preds)

            # 保存结果
            result_df = pd.DataFrame({'Predicted_Class': pred_labels})
            if has_label:
                result_df['True_Class'] = y_true.values
                result_df['Correct'] = result_df['Predicted_Class'] == result_df['True_Class']
                accuracy = result_df['Correct'].mean()
                print(f"\n准确率: {accuracy:.2%}")

            result_df.to_csv(args.output, index=False)
            print(f"\n✅ 预测结果已保存: {args.output}")

        except FileNotFoundError as e:
            print(f"❌ 文件未找到: {e}")
        except Exception as e:
            print(f"❌ 预测失败: {e}")


if __name__ == '__main__':
    main()