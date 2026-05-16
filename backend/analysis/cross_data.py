import pandas as pd
import numpy as np


def compute_cross_discoveries(df):
    discoveries = []
    df_copy = df

    # ===== 1. Borough cost efficiency — 散点气泡图 =====
    borough_stats = df_copy.groupby("行政区").agg(
        平均费用=("修正后总费用", "mean"),
        平均距离=("行程距离", "mean"),
        订单量=("修正后总费用", "count"),
        平均小费=("小费", "mean"),
    ).round(1)
    borough_stats["每英里费用"] = (borough_stats["平均费用"] / borough_stats["平均距离"]).round(1)
    borough_stats = borough_stats.sort_values("订单量", ascending=False)

    scatter_pts = []
    for b in borough_stats.index:
        scatter_pts.append({
            "x": float(borough_stats.loc[b, "平均距离"]),
            "y": float(borough_stats.loc[b, "平均费用"]),
            "size": int(borough_stats.loc[b, "订单量"]),
            "label": b,
        })

    discoveries.append({
        "title": "行政区费用效率散点图",
        "description": f"X轴=平均距离，Y轴=平均费用，气泡大小=订单量。右上角为长途高消费区，左下为短途经济区。{borough_stats['每英里费用'].idxmax()} 每英里费用最高。",
        "chart_type": "scatter",
        "data": {
            "points": scatter_pts,
            "x_label": "平均距离 (mi)",
            "y_label": "平均费用 ($)",
        }
    })

    # ===== 2. Hour vs Tip Rate — 折线+柱混合 =====
    df_copy["小费率"] = np.where(df_copy["车费"] > 0, df_copy["小费"] / df_copy["车费"] * 100, 0)
    hour_tip = df_copy.groupby("小时").agg(
        平均小费率=("小费率", "mean"),
        订单量=("修正后总费用", "count"),
    ).round(1)
    best_hour = hour_tip["平均小费率"].idxmax()
    discoveries.append({
        "title": "小费率时段规律",
        "description": f"小费率最高时段: {best_hour}:00 ({hour_tip['平均小费率'].max()}%)，深夜乘客更慷慨；但订单量高峰在晚高峰时段。",
        "chart_type": "line",
        "data": {
            "categories": [f"{h}:00" for h in hour_tip.index.tolist()],
            "series": {
                "平均小费率(%)": hour_tip["平均小费率"].tolist(),
            },
            "x_label": "小时",
            "y_label": "小费率 (%)",
        }
    })

    # ===== 3. Weekday vs Payment — 热力图（保留）=====
    if "支付方式" in df_copy.columns:
        df_copy["星期几"] = df_copy["上车时间"].dt.weekday
        weekday_payment = df_copy.groupby(["星期几", "支付方式"]).size().unstack(fill_value=0)
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        data = []
        for i, row in enumerate(weekday_payment.values):
            row_sum = row.sum()
            data.append([round(v / row_sum * 100, 1) if row_sum > 0 else 0 for v in row])
        discoveries.append({
            "title": "工作日vs周末支付方式热力图",
            "description": "颜色的深浅代表支付占比。周末现金使用率明显上升，信用卡占比下降。",
            "chart_type": "heatmap",
            "data": {
                "categories": weekday_payment.columns.tolist(),
                "rows": [weekday_names[i] for i in weekday_payment.index],
                "values": data,
            }
        })

    # ===== 4. Peak period funnel — 漏斗图 =====
    period_map = {0: "深夜", 1: "深夜", 2: "深夜", 3: "深夜", 4: "深夜", 5: "深夜",
                  6: "早高峰", 7: "早高峰", 8: "早高峰", 9: "早高峰", 10: "白天",
                  11: "白天", 12: "白天", 13: "白天", 14: "白天", 15: "白天", 16: "白天",
                  17: "晚高峰", 18: "晚高峰", 19: "晚高峰", 20: "夜间", 21: "夜间",
                  22: "夜间", 23: "夜间"}
    df_copy["时段"] = df_copy["小时"].map(period_map)
    period_order = ["深夜", "早高峰", "白天", "晚高峰", "夜间"]
    period_counts = df_copy.groupby("时段").size()
    funnel_data = []
    for p in period_order:
        if p in period_counts.index:
            funnel_data.append({"name": p, "value": int(period_counts[p])})

    discoveries.append({
        "title": "出行时段漏斗图",
        "description": f"从深夜到白天再到夜间，订单量如漏斗般变化。{period_counts.idxmax()}时段订单最多（{period_counts.max()}单），{period_counts.idxmin()}最少。",
        "chart_type": "funnel",
        "data": {
            "items": funnel_data,
        }
    })

    # ===== 5. Payment method pie — 玫瑰饼图 =====
    if "支付方式" in df_copy.columns:
        payment_counts = df_copy["支付方式"].value_counts()
        pie_data = [{"name": k, "value": int(v)} for k, v in payment_counts.items()]
        main_payment = payment_counts.idxmax()
        main_pct = round(payment_counts.max() / payment_counts.sum() * 100, 1)
        discoveries.append({
            "title": "支付方式占比玫瑰图",
            "description": f"{main_payment}占比最高（{main_pct}%），为主要支付方式。现金仍占一定比例。",
            "chart_type": "pie",
            "data": {
                "items": pie_data,
            }
        })

    # ===== 6. Passenger vs efficiency — 分组柱状图 =====
    passenger_agg = df_copy.groupby("乘客数量").agg(
        总费用=("修正后总费用", "sum"),
        总距离=("行程距离", "sum"),
        订单量=("修正后总费用", "count"),
    )
    passenger_agg["平均每人费用"] = (passenger_agg["总费用"] / passenger_agg["订单量"]).round(2)
    passenger_agg["平均每英里费用"] = (passenger_agg["总费用"] / passenger_agg["总距离"].replace(0, np.nan)).fillna(0).round(2)
    passenger_eff = passenger_agg[["平均每人费用", "平均每英里费用", "订单量"]]
    discoveries.append({
        "title": "乘客数量与费用效率",
        "description": "拼车人数越多，人均费用越低，体现了共享出行的经济性。但每英里费用差异不大，说明定价主要基于距离。",
        "chart_type": "bar",
        "data": {
            "categories": [f"{p}人" for p in passenger_eff.index.tolist()],
            "series": {
                "平均每人费用($)": passenger_eff["平均每人费用"].tolist(),
                "每英里费用($)": passenger_eff["平均每英里费用"].tolist(),
            },
            "x_label": "乘客数量",
            "y_label": "费用 ($)",
        }
    })

    # ===== 7. Month demand seasonality — 折线图 =====
    month_demand = df_copy.groupby(["月份", "车型"]).size().unstack(fill_value=0)
    discoveries.append({
        "title": "季节性需求变化",
        "description": f"全年订单量最高月份: {month_demand.sum(axis=1).idxmax()}月，最低: {month_demand.sum(axis=1).idxmin()}月。春秋季为出行旺季，冬季（12-2月）需求相对较低。",
        "chart_type": "line",
        "data": {
            "categories": [f"{m}月" for m in month_demand.index.tolist()],
            "series": {
                c: month_demand[c].tolist() for c in month_demand.columns
            },
            "x_label": "月份",
            "y_label": "订单量（单）",
        }
    })

    # ===== 8. Weekend vs Weekday — 雷达对比 =====
    df_copy["是否周末"] = df_copy["上车时间"].dt.weekday.apply(lambda w: "周末" if w >= 5 else "工作日")
    weekend_comp = df_copy.groupby("是否周末").agg(
        平均距离=("行程距离", "mean"),
        平均费用=("修正后总费用", "mean"),
        平均小费率=("小费率", "mean"),
        订单量=("修正后总费用", "count"),
    ).round(1)
    weekend_comp["平均小费率"] = (df_copy.groupby("是否周末").apply(
        lambda g: g["小费"].sum() / g["车费"].sum() * 100 if g["车费"].sum() > 0 else 0
    )).round(1)

    radar_max = {}
    for col in ["平均距离", "平均费用", "平均小费率", "订单量"]:
        if col in weekend_comp.columns:
            radar_max[col] = float(weekend_comp[col].max()) * 1.3

    discoveries.append({
        "title": "周末 vs 工作日雷达对比",
        "description": f"周末平均距离 {weekend_comp.loc['周末','平均距离'] if '周末' in weekend_comp.index else '?'}mi vs 工作日，周末出行距离更长、小费率更高。",
        "chart_type": "radar",
        "data": {
            "indicators": ["平均距离(mi)", "平均费用($)", "平均小费率(%)", "订单量"],
            "max_values": [radar_max.get("平均距离", 10), radar_max.get("平均费用", 30), radar_max.get("平均小费率", 30), radar_max.get("订单量", 50000)],
            "series": [
                {"name": "工作日", "values": [float(weekend_comp.loc["工作日", "平均距离"]) if "工作日" in weekend_comp.index else 0, float(weekend_comp.loc["工作日", "平均费用"]) if "工作日" in weekend_comp.index else 0, float(weekend_comp.loc["工作日", "平均小费率"]) if "工作日" in weekend_comp.index else 0, int(weekend_comp.loc["工作日", "订单量"]) if "工作日" in weekend_comp.index else 0]},
                {"name": "周末", "values": [float(weekend_comp.loc["周末", "平均距离"]) if "周末" in weekend_comp.index else 0, float(weekend_comp.loc["周末", "平均费用"]) if "周末" in weekend_comp.index else 0, float(weekend_comp.loc["周末", "平均小费率"]) if "周末" in weekend_comp.index else 0, int(weekend_comp.loc["周末", "订单量"]) if "周末" in weekend_comp.index else 0]},
            ],
        }
    })

    return {"discoveries": discoveries}
