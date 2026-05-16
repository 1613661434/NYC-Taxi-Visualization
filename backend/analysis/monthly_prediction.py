import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


def _fit_and_predict(months, values, degree=3):
    """用前11个月的多项式拟合，预测第12个月"""
    train_months = months[:11]
    train_values = values[:11]
    actual_12 = values[11]

    coeffs = np.polyfit(train_months, train_values, degree)
    poly = np.poly1d(coeffs)

    fitted = [round(float(poly(m)), 0) for m in months]
    predicted = fitted[-1]

    residual = actual_12 - predicted
    residual_pct = round(float(residual / actual_12 * 100), 1) if actual_12 != 0 else 0

    return {
        "months": [int(m) for m in months],
        "actual": [round(float(v), 0) for v in values],
        "fitted": fitted,
        "predicted": predicted,
        "actual_12": round(float(actual_12), 0),
        "residual": round(float(residual), 0),
        "residual_pct": residual_pct,
    }


def _analyze_difference(name, unit, predicted, actual_12, residual_pct):
    """生成差异分析文字"""
    diff = predicted - actual_12
    abs_pct = abs(residual_pct)
    if abs_pct < 5:
        quality = "预测非常准确，12月数据与历史趋势高度吻合，季节性模式稳定。"
    elif abs_pct < 15:
        direction = "高估" if diff > 0 else "低估"
        quality = f"预测{direction}了{abs_pct}%，12月存在一定偏差，可能受节假日、天气或特殊事件影响。"
    else:
        direction = "高估" if diff > 0 else "低估"
        quality = f"预测{direction}了{abs_pct}%，偏差较大。12月通常为节假日高峰，出行模式与1~11月显著不同，多项式外推难以捕捉此类突变。"

    return f"{name}预测值 {predicted} {unit}，实际值 {actual_12} {unit}，偏差 {residual_pct}%。{quality}"


def _distance_fare_regression(df, taxi_type, sample_n=600):
    """距离 vs 费用 线性回归分析"""
    sub = df[df["车型"] == taxi_type][["行程距离", "修正后总费用"]].dropna()
    if len(sub) < 50:
        return None

    X = sub[["行程距离"]].values
    y = sub["修正后总费用"].values

    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    r2 = round(float(r2_score(y, y_pred)), 4)
    slope = round(float(model.coef_[0]), 4)
    intercept = round(float(model.intercept_), 2)

    # 采样散点用于图表
    n = min(sample_n, len(sub))
    indices = np.random.choice(len(sub), n, replace=False)
    scatter_points = []
    for i in indices:
        scatter_points.append({
            "distance": round(float(X[i][0]), 2),
            "fare": round(float(y[i]), 2),
        })

    # 回归线端点
    x_min, x_max = float(X.min()), float(X.max())
    line_points = [
        {"distance": round(x_min, 1), "fare": round(float(model.predict([[x_min]])[0]), 2)},
        {"distance": round(x_max, 1), "fare": round(float(model.predict([[x_max]])[0]), 2)},
    ]

    analysis = (
        f"行程距离与总费用呈线性关系，R²={r2}，斜率={slope}（每增加1英里费用增加${slope}），"
        f"截距={intercept}（起步价/固定费用约${intercept}）。"
    )
    if r2 > 0.8:
        analysis += "模型解释力很强，距离是费用的主要决定因素。"
    elif r2 > 0.5:
        analysis += "距离能解释大部分费用变化，但仍有其他因素（时段、拥堵、小费等）在起作用。"
    else:
        analysis += "距离对费用的解释力一般，费用受多种复杂因素（车型、区域、时段、拥堵等）综合影响。"

    return {
        "scatter": scatter_points,
        "regression_line": line_points,
        "r2": r2,
        "slope": slope,
        "intercept": intercept,
        "analysis": analysis,
    }


def compute_monthly_prediction(df):
    # ===== 第一页：月度订单量时序预测 =====
    monthly = df.groupby(["月份", "车型"]).agg(
        订单量=("修正后总费用", "count"),
    ).reset_index()

    def build_type_data(taxi_type):
        data = monthly[monthly["车型"] == taxi_type].sort_values("月份")
        if len(data) < 12:
            return None
        trips_result = _fit_and_predict(data["月份"].values, data["订单量"].values)
        trips_result["analysis"] = _analyze_difference(
            "订单量", "单", trips_result["predicted"], trips_result["actual_12"], trips_result["residual_pct"]
        )
        return {"trips": trips_result}

    result = {}
    yellow_data = build_type_data("黄色出租车")
    green_data = build_type_data("绿色出租车")
    if yellow_data:
        result["yellow"] = yellow_data
    if green_data:
        result["green"] = green_data

    # 总体（黄+绿）月度订单预测
    total_monthly = df.groupby("月份").agg(订单量=("修正后总费用", "count")).sort_index()
    if len(total_monthly) >= 12:
        total_trips = _fit_and_predict(total_monthly.index.values, total_monthly["订单量"].values)
        total_trips["analysis"] = _analyze_difference(
            "总体订单量", "单", total_trips["predicted"], total_trips["actual_12"], total_trips["residual_pct"]
        )
        result["total"] = {"trips": total_trips}

    # ===== 第二页：距离 vs 费用 回归分析 =====
    for taxi_type, key in [("黄色出租车", "yellow"), ("绿色出租车", "green")]:
        reg = _distance_fare_regression(df, taxi_type)
        if reg and key in result:
            result[key]["distance_fare_regression"] = reg
        elif reg:
            result[key] = {"distance_fare_regression": reg}

    return result
