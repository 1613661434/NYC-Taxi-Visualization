import pandas as pd
import numpy as np


def compute_preferences(df):
    results = {}

    # 1. Payment by borough
    if "支付方式" in df.columns:
        payment_borough = df.groupby(["行政区", "支付方式"]).size().unstack(fill_value=0)
        results["payment_by_borough"] = {
            "boroughs": payment_borough.index.tolist(),
            "categories": payment_borough.columns.tolist(),
            "data": payment_borough.values.tolist(),
        }

    # 2. Tip rate by time period
    period_map = {0: "深夜", 1: "深夜", 2: "深夜", 3: "深夜", 4: "深夜", 5: "深夜",
                  6: "早高峰", 7: "早高峰", 8: "早高峰", 9: "早高峰", 10: "白天",
                  11: "白天", 12: "白天", 13: "白天", 14: "白天", 15: "白天", 16: "白天",
                  17: "晚高峰", 18: "晚高峰", 19: "晚高峰", 20: "夜间", 21: "夜间",
                  22: "夜间", 23: "夜间"}
    df_copy = df  # 不需要 copy，load_full_data 已返回副本
    df_copy["时段"] = df_copy["小时"].map(period_map)
    df_copy["小费率"] = np.where(df_copy["车费"] > 0, df_copy["小费"] / df_copy["车费"] * 100, 0)
    tip_by_period = df_copy.groupby(["时段", "车型"])["小费率"].mean().round(1).unstack(fill_value=0)
    results["tip_by_period"] = {
        "periods": tip_by_period.index.tolist(),
        "categories": tip_by_period.columns.tolist(),
        "data": tip_by_period.values.tolist(),
    }

    # 3. Distance by hour
    dist_by_hour = df_copy.groupby(["小时", "车型"])["行程距离"].mean().round(1).unstack(fill_value=0)
    results["distance_by_hour"] = {
        "hours": dist_by_hour.index.tolist(),
        "categories": dist_by_hour.columns.tolist(),
        "data": dist_by_hour.values.tolist(),
    }

    # 4. Peak vs off-peak
    df_copy["高峰"] = df_copy["小时"].apply(lambda h: "高峰" if h in [7, 8, 9, 17, 18, 19] else "非高峰")
    peak = df_copy.groupby("高峰").agg(
        平均费用=("修正后总费用", "mean"),
        平均距离=("行程距离", "mean"),
        平均小费率=("小费率", "mean"),
        订单量=("修正后总费用", "count"),
    ).round(1)
    results["peak_vs_offpeak"] = {
        "categories": peak.index.tolist(),
        "metrics": peak.columns.tolist(),
        "data": peak.values.tolist(),
    }

    # 5. Passenger preference
    passenger_period = df_copy.groupby(["乘客数量", "车型"]).size().unstack(fill_value=0)
    results["passenger_by_taxi_type"] = {
        "passengers": passenger_period.index.tolist(),
        "categories": passenger_period.columns.tolist(),
        "data": passenger_period.values.tolist(),
    }

    # 6. Payment by taxi type
    if "支付方式" in df.columns:
        payment_taxi = df.groupby(["车型", "支付方式"]).size().unstack(fill_value=0)
        results["payment_by_taxi_type"] = {
            "taxi_types": payment_taxi.index.tolist(),
            "categories": payment_taxi.columns.tolist(),
            "data": payment_taxi.values.tolist(),
        }

    return results
