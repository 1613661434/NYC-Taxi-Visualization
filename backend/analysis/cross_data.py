import pandas as pd
import numpy as np


def compute_cross_discoveries(df):
    discoveries = []
    df_copy = df.copy()

    # 1. Borough vs Avg Fare
    borough_fare = df_copy.groupby("行政区").agg(
        平均费用=("修正后总费用", "mean"),
        平均距离=("行程距离", "mean"),
        订单量=("修正后总费用", "count"),
        平均小费=("小费", "mean"),
    ).round(1)
    borough_fare["每英里费用"] = (borough_fare["平均费用"] / borough_fare["平均距离"]).round(1)
    borough_fare = borough_fare.sort_values("平均费用", ascending=False)

    discoveries.append({
        "title": "行政区费用效率对比",
        "description": f"平均费用最高的行政区: {borough_fare.index[0]} (${borough_fare['平均费用'].iloc[0]})，最低: {borough_fare.index[-1]} (${borough_fare['平均费用'].iloc[-1]})",
        "chart_type": "bar",
        "data": {
            "categories": borough_fare.index.tolist(),
            "series": {
                "平均费用($)": borough_fare["平均费用"].tolist(),
                "每英里费用($)": borough_fare["每英里费用"].tolist(),
            }
        }
    })

    # 2. Hour vs Tip Rate
    df_copy["小费率"] = np.where(df_copy["车费"] > 0, df_copy["小费"] / df_copy["车费"] * 100, 0)
    hour_tip = df_copy.groupby("小时").agg(
        平均小费率=("小费率", "mean"),
        平均费用=("修正后总费用", "mean"),
        订单量=("修正后总费用", "count"),
    ).round(1)
    best_hour = hour_tip["平均小费率"].idxmax()
    discoveries.append({
        "title": "小费率时段规律",
        "description": f"小费率最高时段: {best_hour}:00 ({hour_tip['平均小费率'].max()}%)，深夜时段乘客更慷慨",
        "chart_type": "line",
        "data": {
            "categories": [f"{h}:00" for h in hour_tip.index.tolist()],
            "series": {
                "平均小费率(%)": hour_tip["平均小费率"].tolist(),
            }
        }
    })

    # 3. Weekday vs Payment
    if "支付方式" in df_copy.columns:
        df_copy["星期几"] = df_copy["上车时间"].dt.weekday
        weekday_payment = df_copy.groupby(["星期几", "支付方式"]).size().unstack(fill_value=0)
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        data = []
        for i, row in enumerate(weekday_payment.values):
            row_sum = row.sum()
            data.append([round(v / row_sum * 100, 1) if row_sum > 0 else 0 for v in row])
        discoveries.append({
            "title": "工作日vs周末支付方式变化",
            "description": "周末信用卡支付比例通常低于工作日，现金使用率上升",
            "chart_type": "heatmap",
            "data": {
                "categories": weekday_payment.columns.tolist(),
                "rows": [weekday_names[i] for i in weekday_payment.index],
                "values": data,
            }
        })

    # 4. Passenger count vs efficiency
    passenger_eff = df_copy.groupby("乘客数量").agg(
        平均每人费用=("修正后总费用", lambda x: x.mean()),
        平均每英里费用=("修正后总费用", lambda x: x.sum() / df_copy.loc[x.index, "行程距离"].sum() if df_copy.loc[x.index, "行程距离"].sum() > 0 else 0),
        订单量=("修正后总费用", "count"),
    ).round(2)
    discoveries.append({
        "title": "乘客数量与费用关系",
        "description": "拼车越多，人均费用越低 — 体现共享经济效应",
        "chart_type": "bar",
        "data": {
            "categories": [f"{p}人" for p in passenger_eff.index.tolist()],
            "series": {
                "平均费用($)": passenger_eff["平均每人费用"].tolist(),
            }
        }
    })

    # 5. Month vs Demand by taxi type
    month_demand = df_copy.groupby(["月份", "车型"]).size().unstack(fill_value=0)
    discoveries.append({
        "title": "季节性需求变化",
        "description": f"全年订单量最高月份: {month_demand.sum(axis=1).idxmax()}月，最低: {month_demand.sum(axis=1).idxmin()}月",
        "chart_type": "line",
        "data": {
            "categories": [f"{m}月" for m in month_demand.index.tolist()],
            "series": {
                c: month_demand[c].tolist() for c in month_demand.columns
            }
        }
    })

    # 6. Weekend vs weekday distance
    df_copy["是否周末"] = df_copy["上车时间"].dt.weekday.apply(lambda w: "周末" if w >= 5 else "工作日")
    weekend_comp = df_copy.groupby("是否周末").agg(
        平均距离=("行程距离", "mean"),
        平均费用=("修正后总费用", "mean"),
        平均小费率=("小费率", "mean"),
    ).round(1)
    discoveries.append({
        "title": "周末vs工作日出行模式",
        "description": f"周末平均距离{weekend_comp['平均距离']['周末']}mi vs 工作日{weekend_comp['平均距离']['工作日']}mi",
        "chart_type": "bar",
        "data": {
            "categories": weekend_comp.index.tolist(),
            "series": {
                "平均距离(mi)": weekend_comp["平均距离"].tolist(),
                "平均费用($)": weekend_comp["平均费用"].tolist(),
            }
        }
    })

    return {"discoveries": discoveries}
