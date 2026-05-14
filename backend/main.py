from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import warnings
import os
import glob

warnings.filterwarnings('ignore')

app = FastAPI(title="NYC Taxi API")

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== 配置 =====================
CONFIG = {
    "clean_data_dir": "../data/clean_data",
    "zone_file_path": "../data/taxi_zone_lookup.csv",
    "sample_size": 10000,  # 抽样数，保证不卡顿
}

# 全局内存缓存（只加载一次）
df_cache = None

# ===================== 仅加载已清洗数据 =====================
def load_cleaned_data():
    global df_cache
    if df_cache is not None:
        return df_cache

    # 加载区域表
    zone_df = pd.read_csv(CONFIG["zone_file_path"]).rename(columns={
        "LocationID": "位置ID", "Borough": "行政区"
    })

    # 读取所有已清洗文件
    files = glob.glob(os.path.join(CONFIG["clean_data_dir"], "*.parquet"))
    if not files:
        raise Exception("❌ 未找到清洗后数据！请先运行 clean_data.py")

    # 轻量抽样加载，不卡电脑
    df_list = []
    for file in files:
        temp_df = pd.read_parquet(file)
        temp_df = temp_df.sample(min(5000, len(temp_df)), random_state=1)
        df_list.append(temp_df)

    df = pd.concat(df_list, ignore_index=True)
    df = df.sample(min(CONFIG["sample_size"], len(df)), random_state=1)
    
    # 数据处理
    df = df.merge(zone_df, left_on="上车区域ID", right_on="位置ID", how="left").dropna(subset=["行政区"])
    df["小时"] = df["上车时间"].dt.hour

    df_cache = df
    print("✅ 数据加载完成")
    return df

# ===================== API接口 =====================
@app.get("/api/taxi-data")
def get_taxi_data():
    df = load_cleaned_data()
    return {
        "company_count": df["车型"].value_counts().to_dict(),
        "hour_trend": df["小时"].value_counts().sort_index().tolist(),
        "borough_top": df["行政区"].value_counts().head(6).to_dict()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)