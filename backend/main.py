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

# ===================== 核心配置（适配你的目录结构） =====================
CONFIG = {
    "raw_data_dir": "./data",
    "clean_data_dir": "./data/clean_data",
    "zone_file_path": "./data/taxi_zone_lookup.csv",
    "target_year": 2018,
    "sample_size": None  # 关闭抽样，清洗全部数据
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

# ===================== 通用工具函数 =====================
def create_dir_if_not_exist(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def standardize_time(df, pickup_col="上车时间", dropoff_col="下车时间"):
    df[pickup_col] = pd.to_datetime(df[pickup_col], errors='coerce')
    df[dropoff_col] = pd.to_datetime(df[dropoff_col], errors='coerce')
    return df

def filter_target_year(df, year, pickup_col="上车时间", dropoff_col="下车时间"):
    df = df[
        (df[pickup_col].dt.year == year) &
        (df[dropoff_col].dt.year == year)
    ]
    return df

def filter_valid_trips(df, pickup_col="上车时间", dropoff_col="下车时间"):
    df = df.dropna(subset=[pickup_col, dropoff_col])
    df = df[df[dropoff_col] > df[pickup_col]]
    return df

def recalculate_total_amount(df, taxi_type):
    cost_cols = ["车费", "额外附加费", "MTA税费", "改善附加费", "小费", "通行费"]
    for col in cost_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)
        else:
            df[col] = 0
    df["修正后总费用"] = df[cost_cols].sum(axis=1)
    return df

def filter_abnormal_values(df):
    df = df[
        (df["乘客数量"].between(1, 6)) &
        (df["行程距离"] > 0) &
        (df["车费"] >= 0) &
        (df["修正后总费用"] >= 0) &
        (df["乘客数量"].notna()) &
        (df["行程距离"].notna())
    ]
    return df

# ===================== 单文件清洗函数（新增原始数据条数统计） =====================
def clean_single_taxi_file(file_path, taxi_type):
    # 1. 加载原始数据并统计条数
    df = pd.read_parquet(file_path)
    raw_count = len(df)  # 原始数据条数
    
    # 2. 字段重命名（保留所有原始列，仅映射指定列）
    rename_map = COLUMN_MAPPING[taxi_type]
    df = df.rename(columns=rename_map)
    
    # 3. 删除重复记录
    df = df.drop_duplicates()
    
    # 4. 时间字段标准化
    df = standardize_time(df)
    
    # 5. 缺失值处理（删除上下车时间为空）
    df = filter_valid_trips(df)
    
    # 6. 时间范围过滤：仅保留目标年份
    df = filter_target_year(df, CONFIG["target_year"])
    
    # 7. 总费用修正（核心）
    df = recalculate_total_amount(df, taxi_type)
    
    # 8. 异常值过滤
    df = filter_abnormal_values(df)
    
    # 9. 添加车型标签
    df["车型"] = taxi_type.capitalize()
    
    clean_count = len(df)  # 清洗后数据条数
    return df, raw_count, clean_count

# ===================== 批量清洗 + 保存（全量数据，不抽样） =====================
def batch_clean_taxi_data():
    create_dir_if_not_exist(CONFIG["clean_data_dir"])
    
    for taxi_type in ["green", "yellow"]:
        # 原始数据路径
        raw_dir = os.path.join(CONFIG["raw_data_dir"], taxi_type)
        # 匹配所有parquet文件
        parquet_files = glob.glob(os.path.join(raw_dir, "*.parquet"))
        
        if not parquet_files:
            print(f"⚠️ 未找到 {taxi_type} 车原始数据文件（路径：{raw_dir}）")
            continue
        
        # 批量处理每个文件
        for file_path in parquet_files:
            try:
                # 清洗数据（获取原始条数+清洗后条数）
                clean_df, raw_count, clean_count = clean_single_taxi_file(file_path, taxi_type)
                
                # 生成保存文件名
                file_name = os.path.basename(file_path)
                save_file_name = f"{taxi_type}_cleaned_{file_name}"
                save_path = os.path.join(CONFIG["clean_data_dir"], save_file_name)
                
                # 保存清洗后的数据（Parquet格式，节省空间）
                clean_df.to_parquet(save_path, index=False)
                
                # 输出增强日志：包含原始条数+清洗后条数
                print(f"✅ 已保存清洗后的数据：{save_path}")
                print(f"   📊 原始数据：{raw_count} 条 | 清洗后：{clean_count} 条 | 过滤掉：{raw_count - clean_count} 条\n")
                
            except Exception as e:
                print(f"❌ 处理文件 {file_path} 失败：{str(e)}\n")

# ===================== 加载清洗后的数据（不合并所有文件） =====================
def load_cleaned_data():
    # 1. 加载区域表
    zone_df = pd.read_csv(CONFIG["zone_file_path"])
    zone_df = zone_df.rename(columns={
        "LocationID": "位置ID",
        "Borough": "行政区",
        "Zone": "区域名称",
        "service_zone": "服务区域"
    })
    
    # 2. 查找清洗后文件
    clean_files = glob.glob(os.path.join(CONFIG["clean_data_dir"], "*.parquet"))
    if not clean_files:
        print("⚠️ 未找到清洗后的数据，先执行批量清洗...")
        batch_clean_taxi_data()
        clean_files = glob.glob(os.path.join(CONFIG["clean_data_dir"], "*.parquet"))
    
    # 3. 只加载第一个文件，不合并！
    df = pd.read_parquet(clean_files[0])
    
    # 4. 关联区域信息
    df = df.merge(zone_df, left_on="上车区域ID", right_on="位置ID", how="left")
    df = df[df["行政区"].notna()]
    
    # 5. 提取小时
    df["小时"] = df["上车时间"].dt.hour
    
    return df

# ===================== API接口 =====================
@app.get("/api/taxi-data")
def get_taxi_data():
    clean_df = load_cleaned_data()
    result = {
        "company_count": clean_df["车型"].value_counts().to_dict(),
        "hour_trend": clean_df["小时"].value_counts().sort_index().tolist(),
        "borough_top": clean_df["行政区"].value_counts().head(6).to_dict()
    }
    return result

@app.get("/api/clean-data")
def trigger_clean_data():
    try:
        batch_clean_taxi_data()
        return {"status": "success", "message": "数据清洗完成，已保存到 data/clean_data 目录"}
    except Exception as e:
        return {"status": "failed", "message": f"清洗失败：{str(e)}"}

# 本地运行
if __name__ == "__main__":
    import uvicorn
    batch_clean_taxi_data()
    uvicorn.run(app, host="0.0.0.0", port=8000)