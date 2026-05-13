from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

app = FastAPI(title="NYC Taxi API")

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== 数据加载 + 完整版数据清洗 =====================
def load_and_clean_data():
    DATA_BASE = "../data/"
    
    # 1. 加载原始数据 + 采样
    zone_df = pd.read_csv(DATA_BASE + "taxi_zone_lookup.csv")
    green_df = pd.read_parquet(DATA_BASE + "green/green_tripdata_2018-01.parquet").sample(5000)
    yellow_df = pd.read_parquet(DATA_BASE + "yellow/yellow_tripdata_2018-01.parquet").sample(5000)

    # 2. 给数据添加公司标签
    green_df["company"] = "Green"
    yellow_df["company"] = "Yellow"

    # 3. 统一时间字段
    green_df["pickup_time"] = pd.to_datetime(green_df["lpep_pickup_datetime"])
    yellow_df["pickup_time"] = pd.to_datetime(yellow_df["tpep_pickup_datetime"])

    # ===================== 核心数据清洗 =====================
    df = pd.concat([green_df, yellow_df], ignore_index=True)

    # 清洗1：剔除无效行程（距离/费用≤0）
    df = df[(df["trip_distance"] > 0) & (df["total_amount"] > 0)]

    # 清洗2：只保留2018年数据
    df = df[df["pickup_time"].dt.year == 2018]

    # 清洗3：删除重复数据
    df = df.drop_duplicates()

    # 清洗4：关联区域表 + 剔除空值
    df = df.merge(zone_df, left_on="PULocationID", right_on="LocationID", how="left")
    df = df[df["Borough"].notna()]

    # 提取小时
    df["hour"] = df["pickup_time"].dt.hour
    # ===================== 清洗完成 =====================
    
    return df

# ===================== API接口 =====================
@app.get("/api/taxi-data")
def get_taxi_data():
    clean_df = load_and_clean_data()

    # 统计数据（传给Vue前端）
    result = {
        "company_count": clean_df["company"].value_counts().to_dict(),
        "hour_trend": clean_df["hour"].value_counts().sort_index().tolist(),
        "borough_top": clean_df["Borough"].value_counts().head(6).to_dict()
    }

    return result