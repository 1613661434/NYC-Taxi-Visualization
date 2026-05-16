import pandas as pd
import numpy as np
from scipy import stats


def compute_advanced_correlation(df):
    # 只取最核心的数值字段
    keep = ["行程距离", "车费", "小费", "乘客数量", "修正后总费用", "小时", "月份",
            "额外附加费", "通行费"]
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cols = [c for c in keep if c in numeric_cols]

    # Pearson 用全量数据（numpy 底层 O(N)，很快）
    sub = df[cols].dropna()
    pearson_matrix = sub.corr(method='pearson').round(4).to_dict()

    # Spearman 用 30K 采样（O(N log N) 排序，30K 统计上足够稳定）
    if len(sub) > 30000:
        sub_sp = sub.sample(30000, random_state=42)
    else:
        sub_sp = sub
    spearman_matrix = sub_sp.corr(method='spearman').round(4).to_dict()

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


def compute_borough_analysis(df):
    """行政区与多维指标的关联分析"""
    boroughs = df.groupby("行政区")

    # 1. 雷达图：各行政区核心指标均值
    metrics = ["修正后总费用", "行程距离", "小费", "乘客数量"]
    metric_names = ["平均费用($)", "平均距离(mi)", "平均小费($)", "平均乘客数"]
    radar_data = {}
    max_vals = {}
    for i, m in enumerate(metrics):
        if m in df.columns:
            series = boroughs[m].mean().round(2)
            name = metric_names[i]
            radar_data[name] = series.to_dict()
            max_vals[name] = float(series.max()) * 1.2

    # 2. 费用效率：每英里费用
    cost_eff = boroughs.agg(
        总费用=("修正后总费用", "sum"),
        总距离=("行程距离", "sum"),
        订单量=("修正后总费用", "count"),
    )
    cost_eff["每英里费用($)"] = (cost_eff["总费用"] / cost_eff["总距离"]).round(2)
    cost_eff["人均费用($)"] = (cost_eff["总费用"] / cost_eff["订单量"]).round(2)

    # 3. 支付方式分布（百分比）
    payment_pct = None
    if "支付方式" in df.columns:
        payment_raw = df.groupby(["行政区", "支付方式"]).size().unstack(fill_value=0)
        payment_pct = payment_raw.div(payment_raw.sum(axis=1), axis=0).round(3)

    # 过滤掉订单太少的行政区（< 10单）
    valid_boroughs = cost_eff[cost_eff["订单量"] >= 10].index.tolist()
    borough_list = [b for b in valid_boroughs if b in radar_data.get("平均费用($)", {})]

    return {
        "boroughs": borough_list,
        "radar": {k: [v.get(b, 0) for b in borough_list] for k, v in radar_data.items()},
        "radar_metrics": list(radar_data.keys()),
        "radar_max": max_vals,
        "cost_efficiency": {
            b: {
                "每英里费用": float(cost_eff.loc[b, "每英里费用($)"]),
                "人均费用": float(cost_eff.loc[b, "人均费用($)"]),
                "订单量": int(cost_eff.loc[b, "订单量"]),
            }
            for b in borough_list if b in cost_eff.index
        },
        "payment_distribution": {
            "boroughs": payment_pct.loc[borough_list].index.tolist() if payment_pct is not None else borough_list,
            "categories": payment_pct.columns.tolist() if payment_pct is not None else [],
            "data": payment_pct.loc[borough_list].values.tolist() if payment_pct is not None else [],
        } if payment_pct is not None else None,
    }
