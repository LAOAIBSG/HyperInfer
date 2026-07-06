import numpy as np
import random
from sklearn.metrics import jaccard_score

def calculate_jaccard_mean(sets):
    """计算集合之间的Jaccard均值"""
    num_sets = len(sets)
    if num_sets < 2:
        return 0
    jaccard_similarities = []
    for i in range(num_sets):
        for j in range(i + 1, num_sets):
            set1 = sets[i]
            set2 = sets[j]
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            jaccard_similarities.append(intersection / union)
    return np.mean(jaccard_similarities)

def random_subset_jaccard_mean(n, x, trials):
    """计算随机选择子集的Jaccard均值"""
    mean_jaccard_similarities = []
    for _ in range(trials):
        subsets = []
        num_elements = int(n * x / 100)
        for _ in range(trials):
            elements = set(random.sample(range(1, n + 1), num_elements))
            subsets.append(elements)
        mean_jaccard = calculate_jaccard_mean(subsets)
        mean_jaccard_similarities.append(mean_jaccard)
    return np.mean(mean_jaccard_similarities)

# 参数设置
n = 100  # 选择1到n的范围
x = 50   # 选择x%个数字
trials = 100  # 重复实验的次数

# 计算Jaccard均值
mean_jaccard = random_subset_jaccard_mean(n, x, trials)
print(f"Jaccard均值: {mean_jaccard:.4f}")
