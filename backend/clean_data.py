import pandas as pd
import os
import glob
import warnings

warnings.filterwarnings('ignore')

# ===================== 核心配置 =====================
CONFIG = {
    "raw_data_dir": "../data",
    "clean_data_dir": "../data/clean_data",
    "zone_file_path": "../data/taxi_zone_lookup.csv",
    "target_year": 2018,
}

# 列名映射配置
COLUMN_MAPPING = {
    "green": {
        "lpep_pickup_datetime": "上车时间",
        "lpep_dropoff_datetime": "下车时间",
        "PULocationID": "上车区域ID",
        "DOLocationID": "下车区域ID",
        "passenger_count": "乘客数量",
        "trip_distance": "行程距离",
        "fare_amount": "车费",
        "extra": "额外附加费",
        "mta_tax": "MTA税费",
        "improvement_surcharge": "改善附加费",
        "tip_amount": "小费",
        "tolls_amount": "通行费",
        "total_amount": "原始总费用",
        "trip_type": "行程类型"
    },
    "yellow": {
        "tpep_pickup_datetime": "上车时间",
        "tpep_dropoff_datetime": "下车时间",
        "PULocationID": "上车区域ID",
        "DOLocationID": "下车区域ID",
        "passenger_count": "乘客数量",
        "trip_distance": "行程距离",
        "fare_amount": "车费",
        "extra": "额外附加费",
        "mta_tax": "MTA税费",
        "improvement_surcharge": "改善附加费",
        "tip_amount": "小费",
        "tolls_amount": "通行费",
        "total_amount": "原始总费用",
        "RatecodeID": "费率类型ID",
        "congestion_surcharge": "拥堵费"
    }
}

# ===================== 工具函数 =====================
def create_dir_if_not_exist(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def standardize_time(df, pickup_col="上车时间", dropoff_col="下车时间"):
    df[pickup_col] = pd.to_datetime(df[pickup_col], errors='coerce')
    df[dropoff_col] = pd.to_datetime(df[dropoff_col], errors='coerce')
    return df

def filter_target_year(df, year, pickup_col="上车时间", dropoff_col="下车时间"):
    df = df[(df[pickup_col].dt.year == year) & (df[dropoff_col].dt.year == year)]
    return df

def filter_valid_trips(df, pickup_col="上车时间", dropoff_col="下车时间"):
    df = df.dropna(subset=[pickup_col, dropoff_col])
    return df[df[dropoff_col] > df[pickup_col]]

def recalculate_total_amount(df):
    cost_cols = ["车费", "额外附加费", "MTA税费", "改善附加费", "小费", "通行费"]
    for col in cost_cols:
        df[col] = df[col].fillna(0) if col in df.columns else 0
    df["修正后总费用"] = df[cost_cols].sum(axis=1)
    return df

def filter_abnormal_values(df):
    return df[
        (df["乘客数量"].between(1, 6)) &
        (df["行程距离"] > 0) &
        (df["车费"] >= 0) &
        (df["修正后总费用"] >= 0) &
        (df["乘客数量"].notna())
    ]

# ===================== 清洗单文件 =====================
def clean_single_taxi_file(file_path, taxi_type):
    df = pd.read_parquet(file_path)
    df = df.rename(columns=COLUMN_MAPPING[taxi_type])
    df = df.drop_duplicates()
    df = standardize_time(df)
    df = filter_valid_trips(df)
    df = filter_target_year(df, CONFIG["target_year"])
    df = recalculate_total_amount(df)
    df = filter_abnormal_values(df)
    df["车型"] = taxi_type.capitalize()
    return df

# ===================== 批量清洗（主函数） =====================
def batch_clean_taxi_data():
    create_dir_if_not_exist(CONFIG["clean_data_dir"])
    print("🚀 开始批量清洗数据...")

    for taxi_type in ["green", "yellow"]:
        raw_dir = os.path.join(CONFIG["raw_data_dir"], taxi_type)
        files = glob.glob(os.path.join(raw_dir, "*.parquet"))
        
        if not files:
            print(f"⚠️ 未找到 {taxi_type} 数据")
            continue

        for f in files:
            try:
                clean_df = clean_single_taxi_file(f, taxi_type)
                save_path = os.path.join(CONFIG["clean_data_dir"], f"{taxi_type}_cleaned_{os.path.basename(f)}")
                clean_df.to_parquet(save_path, index=False)
                print(f"✅ 已清洗保存: {os.path.basename(save_path)}")
            except Exception as e:
                print(f"❌ 失败: {e}")

    print("\n🎉 所有数据清洗完成！")

# 直接运行此脚本执行清洗
if __name__ == "__main__":
    batch_clean_taxi_data()