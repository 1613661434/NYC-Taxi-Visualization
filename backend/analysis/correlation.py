import pandas as pd
import numpy as np
from scipy import stats


def compute_advanced_correlation(df):
    # 只取最核心的数值字段
    keep = ["行程距离", "车费", "小费", "乘客数量", "修正后总费用", "小时", "月份",
            "额外附加费", "通行费"]
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cols = [c for c in keep if c in numeric_cols]

    # 用 pandas 内置 corr() 快速计算 Pearson 矩阵（numpy 底层，很快）
    sub = df[cols].dropna()
    pearson_matrix = sub.corr(method='pearson').round(4).to_dict()

    # Spearman 也用 pandas 内置
    spearman_matrix = sub.corr(method='spearman').round(4).to_dict()

    # 只对 top pairs 算 p-value（避免 169 次 scipy 调用）
    top_pairs = []
    for i, c1 in enumerate(cols):
        for c2 in cols[i + 1:]:
            pearson_val = pearson_matrix[c1].get(c2) or pearson_matrix[c2].get(c1, 0)
            top_pairs.append({"col1": c1, "col2": c2, "pearson": pearson_val})
    top_pairs.sort(key=lambda x: abs(x["pearson"]), reverse=True)
    top_pairs = top_pairs[:10]

    # 只对 top 5 对计算 p-value 和散点数据
    pvalue_matrix = {c: {c2: 1.0 for c2 in cols} for c in cols}
    scatter_data = {}
    for pair in top_pairs[:5]:
        c1, c2 = pair["col1"], pair["col2"]
        valid = sub[[c1, c2]].dropna()
        if len(valid) > 10:
            _, p = stats.pearsonr(valid[c1].values, valid[c2].values)
            pvalue_matrix[c1][c2] = round(float(p), 6)
            sample = valid.sample(min(300, len(valid)))
            scatter_data[f"{c1}|{c2}"] = [
                {"x": float(sample.iloc[i][c1]), "y": float(sample.iloc[i][c2])}
                for i in range(len(sample))
            ]

    # 补全 spearman 给 top_pairs
    for pair in top_pairs:
        pair["spearman"] = spearman_matrix[pair["col1"]].get(pair["col2"]) or spearman_matrix[pair["col2"]].get(pair["col1"], 0)
        pair["pvalue"] = pvalue_matrix[pair["col1"]].get(pair["col2"], 1)

    return {
        "columns": cols,
        "pearson": pearson_matrix,
        "spearman": spearman_matrix,
        "pvalue": pvalue_matrix,
        "top_pairs": top_pairs,
        "scatter_data": scatter_data,
    }
