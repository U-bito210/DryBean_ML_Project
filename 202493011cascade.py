# -*- coding: utf-8 -*-
"""
网络级联过程仿真（线性阈值模型）
作业：计算思维在社会科学中的应用
算法思路：
1. 根据邻接矩阵构建无向图（若为有向图，可调整邻居计算方式）。
2. 给定初始激活节点集合 S，所有 S 中节点在第一轮前已激活。
3. 每一轮，对所有未激活节点 v：
   - 统计 v 的所有邻居中当前已激活的个数 active_neighbors。
   - 若 active_neighbors / degree(v) >= q（q 为门槛比例），则 v 在本轮被激活。
4. 重复步骤 3，直到某一轮没有新节点激活为止。
5. 输出每一轮新激活的节点列表（按升序排列），并在最后输出总活跃节点。

输入方式：
- 邻接矩阵：从文本文件读取，支持逗号或空格分隔，0/1 表示无/有边。
- 初始节点集 S：在代码中直接修改变量 S 的值，或通过命令行参数传入（此处提供两种方式）。
- 门槛值 q：在代码中直接赋值，或通过命令行参数传入。

注意：若节点度数为 0（孤立点），则永远不会被激活（因为分母为 0）。
"""

import numpy as np
import sys

def read_adjacency_matrix(filename):
    """
    从文件读取邻接矩阵，支持空格或逗号分隔。
    返回 numpy 二维数组。
    """
    try:
        data = np.loadtxt(filename, delimiter=None)  # 自动识别分隔符
        # 确保为方阵
        if data.shape[0] != data.shape[1]:
            raise ValueError("邻接矩阵不是方阵，请检查文件内容。")
        # 将非零值转为 1（如为有权图，可保留权重，但本模型仅使用 0/1）
        A = (data != 0).astype(int)
        return A
    except Exception as e:
        print(f"读取文件 {filename} 失败: {e}")
        sys.exit(1)

def cascade(A, S, q):
    """
    执行级联过程
    参数：
        A : numpy 二维数组，邻接矩阵 (n x n)
        S : list，初始激活节点索引 (从 0 开始)
        q : float，门槛值，0 <= q <= 1
    返回：无（直接打印每步结果）
    """
    n = A.shape[0]
    active = set(S)           # 当前所有活跃节点
    degree = np.sum(A, axis=1)  # 每个节点的度数
    new_active = set(S)       # 上一次新增的节点（初始为 S）
    step = 0

    print(f"初始激活节点: {sorted(new_active)}")
    print("开始级联...")

    while new_active:
        step += 1
        next_new = set()
        # 遍历所有未激活节点
        for v in range(n):
            if v in active:
                continue
            # 孤立节点跳过
            if degree[v] == 0:
                continue
            # 计算活跃邻居数
            neighbors = np.where(A[v] == 1)[0]
            active_neighbors = sum(1 for u in neighbors if u in active)
            # 门槛判定
            if active_neighbors / degree[v] >= q:
                next_new.add(v)
        # 若无新增，终止
        if not next_new:
            break
        # 更新活跃集合
        active.update(next_new)
        new_active = next_new
        print(f"第 {step} 步新增节点: {sorted(new_active)}")

    print(f"级联结束。总活跃节点: {sorted(active)} (共 {len(active)} 个)")

def main():
    # ====== 用户配置区域（请在此修改输入参数） ======
    # 1. 邻接矩阵文件路径（请替换为您的文件）
    matrix_file = "matrix1.txt"   # 可以改为 matrix2.txt 或 matrix3.txt

    # 2. 初始激活节点集（请根据您的数据修改索引，从 0 开始）
    S = [0, 2, 5]   # 示例，请替换

    # 3. 门槛值 q（0~1）
    q = 0.4
    # =============================================

    # 读取邻接矩阵
    A = read_adjacency_matrix(matrix_file)
    print(f"成功读取邻接矩阵，维度: {A.shape[0]} x {A.shape[1]}")

    # 检查 S 中节点是否有效
    n = A.shape[0]
    S = [s for s in S if 0 <= s < n]
    if not S:
        print("初始节点集为空或全部无效，程序退出。")
        return

    # 执行级联
    cascade(A, S, q)

if __name__ == "__main__":
    main()