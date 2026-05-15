from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
import warnings
from functools import lru_cache

warnings.filterwarnings('ignore')

from data_loader import load_cleaned_data, load_full_data, apply_filters, load_zone_lookup
from analysis.missing_values import analyze_missing_values
from analysis.clustering import compute_clustering
from analysis.prediction import train_prediction_model
from analysis.preference import compute_preferences
from analysis.correlation import compute_advanced_correlation
from analysis.cross_data import compute_cross_discoveries

app = FastAPI(title="NYC Taxi API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_filtered_df(use_full=False):
    if use_full:
        df = load_full_data(sample_size=80000)
    else:
        df = load_cleaned_data()
    return df


# ========== 持久化 API 响应缓存（只算一次，重启不丢）==========
import os as _os
import pickle as _pickle

_CACHE_DIR = "../data/cache"
_CACHE_FILE = _os.path.join(_CACHE_DIR, "api_cache.pkl")
_response_cache = {}

def _load_disk_cache():
    global _response_cache
    if _os.path.exists(_CACHE_FILE):
        try:
            with open(_CACHE_FILE, "rb") as f:
                _response_cache = _pickle.load(f)
        except Exception:
            _response_cache = {}

def _save_disk_cache():
    _os.makedirs(_CACHE_DIR, exist_ok=True)
    with open(_CACHE_FILE, "wb") as f:
        _pickle.dump(_response_cache, f)

def cached(key_prefix: str, start_month, end_month, company, borough, compute_fn, min_rows=0):
    """用筛选参数做缓存key，相同筛选不重复计算。结果持久化到磁盘"""
    cache_key = f"{key_prefix}|{start_month}|{end_month}|{company}|{borough}"
    if cache_key in _response_cache:
        return _response_cache[cache_key]
    df = get_filtered_df(use_full=True)
    df = apply_filters(df, start_month, end_month, company, borough)
    if min_rows and len(df) < min_rows:
        return {"error": "数据量不足"}
    result = compute_fn(df)
    _response_cache[cache_key] = result
    _save_disk_cache()
    return result

# 启动时加载磁盘缓存
_load_disk_cache()


# ========== 现有端点 ==========

@app.get("/api/dashboard-data")
def get_dashboard(
    start_month: int = Query(1, ge=1, le=12),
    end_month: int = Query(12, ge=1, le=12),
    company: str = Query(""),
    borough: str = Query("")
):
    df = get_filtered_df(use_full=False)
    df = apply_filters(df, start_month, end_month, company, borough)

    if df.empty:
        return {
            "kpi": {"总行程数": 0, "总营收(万美元)": 0, "平均小费率(%)": 0, "平均行程(英里)": 0, "平均费用($)": 0, "晚高峰占比(%)": 0},
            "company_compare": {}, "borough_dist": {}, "hourly_trend": {}, "fare_level_dist": {}, "payment_dist": {},
            "weekday_trend": {}, "period_dist": {}, "passenger_dist": {}, "yellow_green_comparison": {}, "correlation": {}
        }

    return {
        "kpi": {
            "总行程数": len(df),
            "总营收(万美元)": round(df["修正后总费用"].sum() / 10000, 1),
            "平均小费率(%)": round(df["小费"].mean() / df["车费"].mean() * 100, 1) if len(df) and df["车费"].mean() > 0 else 0,
            "平均行程(英里)": round(df["行程距离"].mean(), 1),
            "平均费用($)": round(df["修正后总费用"].mean(), 1),
            "晚高峰占比(%)": round(len(df[df["小时"].between(17, 19)]) / len(df) * 100, 1) if len(df) else 0
        },
        "company_compare": df["车型"].value_counts().to_dict(),
        "borough_dist": df["行政区"].value_counts().to_dict(),
        "hourly_trend": df["小时"].value_counts().sort_index().to_dict(),
        "fare_level_dist": pd.cut(df["修正后总费用"], [0, 5, 10, 20, 30, 50, 1000], labels=["0-5", "5-10", "10-20", "20-30", "30-50", "50+"]).value_counts().to_dict(),
        "payment_dist": df.get("支付方式", pd.Series([0])).value_counts().to_dict(),
        "weekday_trend": df["上车时间"].dt.weekday.value_counts().sort_index().to_dict(),
        "period_dist": pd.cut(df["小时"], [0, 6, 10, 16, 20, 24], labels=["深夜", "早高峰", "白天", "晚高峰", "夜间"]).value_counts().to_dict(),
        "passenger_dist": df["乘客数量"].value_counts().sort_index().to_dict(),
        "yellow_green_comparison": {
            "平均费用": df.groupby("车型")["修正后总费用"].mean().round(1).to_dict(),
            "平均距离": df.groupby("车型")["行程距离"].mean().round(1).to_dict(),
            "平均小费": df.groupby("车型")["小费"].mean().round(1).to_dict()
        },
        "correlation": df[["行程距离", "车费", "小费", "乘客数量", "修正后总费用"]].corr().round(2).to_dict()
    }


# ========== Req 1: 缺失值分析 ==========

@app.get("/api/missing-values")
def get_missing_values(
    start_month: int = Query(1, ge=1, le=12),
    end_month: int = Query(12, ge=1, le=12),
    company: str = Query(""),
    borough: str = Query("")
):
    return cached("missing", start_month, end_month, company, borough, analyze_missing_values)


# ========== Req 2+3: 聚类分析 ==========

@app.get("/api/clustering")
def get_clustering(
    start_month: int = Query(1, ge=1, le=12),
    end_month: int = Query(12, ge=1, le=12),
    company: str = Query(""),
    borough: str = Query("")
):
    return cached("clustering", start_month, end_month, company, borough, compute_clustering, min_rows=100)


# ========== Req 4: 预测建模 ==========

@app.get("/api/prediction/train")
def get_prediction_train(
    start_month: int = Query(1, ge=1, le=12),
    end_month: int = Query(12, ge=1, le=12),
    company: str = Query(""),
    borough: str = Query("")
):
    return cached("pred_train", start_month, end_month, company, borough, train_prediction_model, min_rows=200)


@app.get("/api/prediction/compare")
def get_prediction_compare(
    start_month: int = Query(1, ge=1, le=12),
    end_month: int = Query(12, ge=1, le=12),
    company: str = Query(""),
    borough: str = Query("")
):
    df = get_filtered_df(use_full=True)
    df = apply_filters(df, start_month, end_month, company, borough)
    if len(df) < 200:
        return {"error": "数据量不足"}
    result = train_prediction_model(df)
    return {"predictions": result["predictions"], "residual_distribution": result["residual_distribution"], "metrics": result["metrics"]}


# ========== Req 5: 偏好分析 ==========

@app.get("/api/preference")
def get_preference(
    start_month: int = Query(1, ge=1, le=12),
    end_month: int = Query(12, ge=1, le=12),
    company: str = Query(""),
    borough: str = Query("")
):
    return cached("preference", start_month, end_month, company, borough, compute_preferences)


# ========== Req 6: 增强相关性 ==========

@app.get("/api/correlation-advanced")
def get_correlation_advanced(
    start_month: int = Query(1, ge=1, le=12),
    end_month: int = Query(12, ge=1, le=12),
    company: str = Query(""),
    borough: str = Query("")
):
    return cached("correlation", start_month, end_month, company, borough, compute_advanced_correlation)


# ========== Req 7: 地图数据 ==========

@app.get("/api/map-data")
def get_map_data(
    start_month: int = Query(1, ge=1, le=12),
    end_month: int = Query(12, ge=1, le=12),
    company: str = Query(""),
    borough: str = Query("")
):
    df = get_filtered_df(use_full=True)
    df = apply_filters(df, start_month, end_month, company, borough)

    pickup = df.groupby("上车区域ID").agg(
        订单量=("修正后总费用", "count"),
        平均费用=("修正后总费用", "mean"),
        平均距离=("行程距离", "mean"),
    ).fillna(0).round(1)
    pickup = pickup.reset_index().rename(columns={"上车区域ID": "location_id"})

    dropoff = df.groupby("下车区域ID").agg(
        订单量=("修正后总费用", "count"),
        平均费用=("修正后总费用", "mean"),
        平均距离=("行程距离", "mean"),
    ).fillna(0).round(1)
    dropoff = dropoff.reset_index().rename(columns={"下车区域ID": "location_id"})

    # Zone name lookup
    zone_df = load_zone_lookup()
    zone_info = zone_df[["位置ID", "行政区", "Zone"]].drop_duplicates(subset=["位置ID"])
    zone_info.columns = ["location_id", "行政区", "zone_name"]

    pickup = pickup.merge(zone_info, on="location_id", how="left").fillna(0)
    dropoff = dropoff.merge(zone_info, on="location_id", how="left").fillna(0)

    return {
        "pickup": pickup.to_dict(orient="records"),
        "dropoff": dropoff.to_dict(orient="records"),
        "max_pickup_count": int(pickup["订单量"].max()) if len(pickup) > 0 else 1,
        "max_dropoff_count": int(dropoff["订单量"].max()) if len(dropoff) > 0 else 1,
    }


# ========== Req 8: 时间轴数据 ==========

@app.get("/api/timeline-data")
def get_timeline_data(
    granularity: str = Query("monthly"),
    start_month: int = Query(1, ge=1, le=12),
    end_month: int = Query(12, ge=1, le=12),
    company: str = Query(""),
    borough: str = Query("")
):
    df = get_filtered_df(use_full=False)
    df = apply_filters(df, 1, 12, company, borough)

    if granularity == "monthly":
        groups = df.groupby("月份")
        buckets = []
        for month, g in groups:
            buckets.append({
                "label": f"{month}月",
                "total_trips": len(g),
                "avg_fare": round(g["修正后总费用"].mean(), 1),
                "avg_distance": round(g["行程距离"].mean(), 1),
                "avg_tip_pct": round(g["小费"].sum() / g["车费"].sum() * 100, 1) if g["车费"].sum() > 0 else 0,
                "yellow": int((g["车型"] == "黄色出租车").sum()),
                "green": int((g["车型"] == "绿色出租车").sum()),
            })
    elif granularity == "hourly":
        groups = df.groupby("小时")
        buckets = []
        for hour, g in groups:
            buckets.append({
                "label": f"{hour}:00",
                "total_trips": len(g),
                "avg_fare": round(g["修正后总费用"].mean(), 1),
                "avg_distance": round(g["行程距离"].mean(), 1),
                "avg_tip_pct": round(g["小费"].sum() / g["车费"].sum() * 100, 1) if g["车费"].sum() > 0 else 0,
                "yellow": int((g["车型"] == "黄色出租车").sum()),
                "green": int((g["车型"] == "绿色出租车").sum()),
            })
    else:  # weekly
        df_week = df.copy()
        df_week["周"] = df_week["上车时间"].dt.isocalendar().week
        groups = df_week.groupby("周")
        buckets = []
        for week, g in groups:
            buckets.append({
                "label": f"第{int(week)}周",
                "total_trips": len(g),
                "avg_fare": round(g["修正后总费用"].mean(), 1),
                "avg_distance": round(g["行程距离"].mean(), 1),
                "avg_tip_pct": round(g["小费"].sum() / g["车费"].sum() * 100, 1) if g["车费"].sum() > 0 else 0,
                "yellow": int((g["车型"] == "黄色出租车").sum()),
                "green": int((g["车型"] == "绿色出租车").sum()),
            })

    return {"buckets": buckets, "granularity": granularity}


# ========== Req 9: 下钻数据 ==========

@app.get("/api/drill-down")
def get_drill_down(
    dimension: str = Query(""),
    value: str = Query(""),
    start_month: int = Query(1, ge=1, le=12),
    end_month: int = Query(12, ge=1, le=12),
    company: str = Query(""),
    borough: str = Query("")
):
    df = get_filtered_df(use_full=False)
    df = apply_filters(df, start_month, end_month, company, borough)

    if dimension == "borough" and value:
        sub = df[df["行政区"] == value]
    elif dimension == "company" and value:
        sub = df[df["车型"] == value]
    elif dimension == "cluster":
        # For cluster drill-down, we recompute clustering on the filtered data
        from analysis.clustering import compute_clustering
        result = compute_clustering(df)
        return result
    else:
        return {"error": "请指定 dimension 和 value"}

    if sub.empty:
        return {"error": "无匹配数据"}

    return {
        "kpi": {
            "总行程数": len(sub),
            "平均费用": round(sub["修正后总费用"].mean(), 1),
            "平均距离": round(sub["行程距离"].mean(), 1),
            "平均小费": round(sub["小费"].mean(), 1),
            "总营收": round(sub["修正后总费用"].sum(), 1),
        },
        "hourly_trend": sub["小时"].value_counts().sort_index().to_dict(),
        "company_compare": sub["车型"].value_counts().to_dict(),
        "fare_level_dist": pd.cut(sub["修正后总费用"], [0, 5, 10, 20, 30, 50, 1000], labels=["0-5", "5-10", "10-20", "20-30", "30-50", "50+"]).value_counts().to_dict(),
        "period_dist": pd.cut(sub["小时"], [0, 6, 10, 16, 20, 24], labels=["深夜", "早高峰", "白天", "晚高峰", "夜间"]).value_counts().to_dict(),
    }


# ========== Req 10: 跨数据关联 ==========

@app.get("/api/cross-correlation")
def get_cross_correlation(
    start_month: int = Query(1, ge=1, le=12),
    end_month: int = Query(12, ge=1, le=12),
    company: str = Query(""),
    borough: str = Query("")
):
    return cached("cross", start_month, end_month, company, borough, compute_cross_discoveries)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
