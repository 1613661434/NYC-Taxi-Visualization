from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import warnings
import os
from datetime import datetime
warnings.filterwarnings('ignore')

app = FastAPI(title="纽约出租车数据可视化API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CACHE_DATA = None
DATA_LOADED = False

# 字段映射（完整保留）
YELLOW_COLS_MAP = {
    'tpep_pickup_datetime': '上车时间',
    'tpep_dropoff_datetime': '下车时间',
    'passenger_count': '乘客数量',
    'trip_distance': '行程距离',
    'PULocationID': '上车区域ID',
    'DOLocationID': '下车区域ID',
    'RateCodeID': '费率类型ID',
    'store_and_fwd_flag': '存储转发标记',
    'payment_type': '支付方式',
    'fare_amount': '车费',
    'extra': '额外附加费',
    'mta_tax': 'MTA税费',
    'tip_amount': '小费',
    'tolls_amount': '通行费',
    'improvement_surcharge': '改善附加费',
    'total_amount': '总费用',
    'congestion_surcharge': '拥堵附加费',
    'airport_fee': '机场费'
}

GREEN_COLS_MAP = {
    'lpep_pickup_datetime': '上车时间',
    'lpep_dropoff_datetime': '下车时间',
    'passenger_count': '乘客数量',
    'trip_distance': '行程距离',
    'PULocationID': '上车区域ID',
    'DOLocationID': '下车区域ID',
    'RateCodeID': '费率类型ID',
    'store_and_fwd_flag': '存储转发标记',
    'payment_type': '支付方式',
    'fare_amount': '车费',
    'extra': '额外附加费',
    'mta_tax': 'MTA税费',
    'tip_amount': '小费',
    'tolls_amount': '通行费',
    'improvement_surcharge': '改善附加费',
    'total_amount': '总费用'
}


def load_and_clean_data(sample_size=30000, months=None, use_cache=True):
    global CACHE_DATA, DATA_LOADED
    if use_cache and DATA_LOADED and CACHE_DATA is not None:
        print("使用缓存数据")
        return CACHE_DATA

    # 自动检测数据目录（与原逻辑相同）
    possible_paths = ["../data/", "./data/", "data/", os.path.join(os.path.dirname(__file__), "../data/")]
    DATA_BASE = None
    for path in possible_paths:
        if os.path.exists(os.path.join(path, "taxi_zone_lookup.csv")):
            DATA_BASE = path
            print(f"找到数据目录: {DATA_BASE}")
            break
    if DATA_BASE is None:
        raise FileNotFoundError("无法找到数据目录")

    if months is None:
        # ========== 改为全年：1-12月 ==========
        months = list(range(1, 13))
    
    print(f"开始加载数据，月份: {months}, 采样大小: {sample_size}")

    zone_df = pd.read_csv(DATA_BASE + "taxi_zone_lookup.csv")
    zone_df = zone_df.rename(columns={
        'LocationID': '区域ID',
        'Borough': '行政区',
        'Zone': '区域名称',
        'service_zone': '服务区'
    })

    green_dfs, yellow_dfs = [], []
    for month in months:
        month_str = f"{month:02d}"
        try:
            green_path = f"{DATA_BASE}green/green_tripdata_2018-{month_str}.parquet"
            print(f"加载绿车: {month_str}月")
            green_temp = pd.read_parquet(green_path)
            if len(green_temp) > sample_size:
                green_temp = green_temp.sample(sample_size, random_state=42)
            existing = [col for col in GREEN_COLS_MAP.keys() if col in green_temp.columns]
            green_temp = green_temp[existing].rename(columns=GREEN_COLS_MAP)
            green_temp['车辆类型'] = '绿色出租车'
            green_temp['上车时间'] = pd.to_datetime(green_temp['上车时间'])
            green_temp['下车时间'] = pd.to_datetime(green_temp['下车时间'])
            green_dfs.append(green_temp)
        except Exception as e:
            print(f"绿车{month_str}月失败: {e}")
        try:
            yellow_path = f"{DATA_BASE}yellow/yellow_tripdata_2018-{month_str}.parquet"
            print(f"加载黄车: {month_str}月")
            yellow_temp = pd.read_parquet(yellow_path)
            if len(yellow_temp) > sample_size:
                yellow_temp = yellow_temp.sample(sample_size, random_state=42)
            existing = [col for col in YELLOW_COLS_MAP.keys() if col in yellow_temp.columns]
            yellow_temp = yellow_temp[existing].rename(columns=YELLOW_COLS_MAP)
            yellow_temp['车辆类型'] = '黄色出租车'
            yellow_temp['上车时间'] = pd.to_datetime(yellow_temp['上车时间'])
            yellow_temp['下车时间'] = pd.to_datetime(yellow_temp['下车时间'])
            yellow_dfs.append(yellow_temp)
        except Exception as e:
            print(f"黄车{month_str}月失败: {e}")

    df = pd.concat(green_dfs + yellow_dfs, ignore_index=True)
    print(f"原始数据合计: {len(df)}条")

    # ========== 以下清洗完全保留原有逻辑 ==========
    df = df[(df['行程距离'] > 0) & (df['总费用'] > 0)]
    if '车费' in df.columns:
        df = df[df['车费'] <= df['总费用']]
    df['行程时长_分钟'] = (df['下车时间'] - df['上车时间']).dt.total_seconds() / 60
    df = df[(df['行程时长_分钟'] > 0) & (df['行程时长_分钟'] <= 120)]
    df['乘客数量'] = df['乘客数量'].fillna(1)
    df = df[(df['乘客数量'] >= 1) & (df['乘客数量'] <= 6)]
    df = df[df['支付方式'].between(1, 6)]
    df = df[df['上车时间'].dt.year == 2018]
    df = df.drop_duplicates(subset=['上车时间', '上车区域ID', '总费用'])
    df = df.merge(zone_df[['区域ID', '行政区', '区域名称']], left_on='上车区域ID', right_on='区域ID', how='left')
    df = df[df['行政区'].notna()]
    df = df[df['总费用'] <= 200]

    df['小时'] = df['上车时间'].dt.hour
    df['星期几'] = df['上车时间'].dt.dayofweek
    df['月份'] = df['上车时间'].dt.month
    df['日期'] = df['上车时间'].dt.date
    df['是否周末'] = df['星期几'].isin([5, 6]).astype(int)
    df['是否晚高峰'] = df['小时'].between(17, 19).astype(int)

    def get_period_detail(hour):
        if 6 <= hour < 10: return '早高峰'
        elif 10 <= hour < 16: return '白天'
        elif 16 <= hour < 20: return '晚高峰'
        elif 20 <= hour < 23: return '夜间'
        else: return '深夜'
    df['时段'] = df['小时'].apply(get_period_detail)

    df['费用等级'] = pd.cut(
        df['总费用'],
        bins=[0, 10, 20, 35, 60, 200],
        labels=['短途(≤$10)', '经济($10-20)', '标准($20-35)', '舒适($35-60)', '豪华(>$60)']
    )

    if '小费' in df.columns and '车费' in df.columns:
        df['小费率'] = (df['小费'] / df['车费'] * 100).round(2)
        df.loc[df['小费率'] > 50, '小费率'] = 50
        df.loc[df['小费率'] < 0, '小费率'] = 0
        df['小费率'] = df['小费率'].fillna(0)

    print(f"清洗完成: {len(df)}条")
    CACHE_DATA = df
    DATA_LOADED = True
    return df


# ========== 所有接口（完整保留，与之前一致）==========
@app.get("/api/taxi-data")
def get_taxi_data():
    df = load_and_clean_data()
    payment_map = {1: "信用卡", 2: "现金", 3: "免付费", 4: "争议", 5: "未知", 6: "已作废"}
    df['支付方式名称'] = df['支付方式'].map(payment_map)
    return {
        "数据概览": {
            "总记录数": len(df),
            "数据起始日期": df["上车时间"].min().strftime("%Y-%m-%d"),
            "数据结束日期": df["上车时间"].max().strftime("%Y-%m-%d")
        },
        "车辆类型统计": df["车辆类型"].value_counts().to_dict(),
        "小时分布": df["小时"].value_counts().sort_index().tolist(),
        "行政区Top6": df["行政区"].value_counts().head(6).to_dict(),
        "支付方式分布": df["支付方式名称"].value_counts().to_dict(),
        "平均指标": {
            "平均行程距离(英里)": round(df["行程距离"].mean(), 2),
            "平均总费用(美元)": round(df["总费用"].mean(), 2),
            "平均小费(美元)": round(df["小费"].mean(), 2) if "小费" in df.columns else 0,
            "平均行程时长(分钟)": round(df["行程时长_分钟"].mean(), 1)
        }
    }

@app.get("/api/hourly-analysis")
def hourly_analysis():
    df = load_and_clean_data()
    hourly_data = []
    for hour in range(24):
        hour_df = df[df["小时"] == hour]
        hourly_data.append({
            "小时": hour,
            "平均费用": round(hour_df["总费用"].mean(), 2) if len(hour_df) > 0 else 0,
            "平均距离": round(hour_df["行程距离"].mean(), 2) if len(hour_df) > 0 else 0,
            "行程数量": len(hour_df)
        })
    yellow_hourly = df[df["车辆类型"] == "黄色出租车"]["小时"].value_counts().sort_index().to_dict()
    green_hourly = df[df["车辆类型"] == "绿色出租车"]["小时"].value_counts().sort_index().to_dict()
    return {"小时级数据": hourly_data, "黄色出租车小时分布": yellow_hourly, "绿色出租车小时分布": green_hourly}

@app.get("/api/borough-analysis")
def borough_analysis():
    df = load_and_clean_data()
    borough_data = []
    for borough in df["行政区"].unique():
        borough_df = df[df["行政区"] == borough]
        borough_data.append({
            "行政区": borough,
            "平均费用": round(borough_df["总费用"].mean(), 2),
            "总费用": round(borough_df["总费用"].sum(), 2),
            "平均距离": round(borough_df["行程距离"].mean(), 2),
            "行程数量": len(borough_df)
        })
    borough_company = pd.crosstab(df["行政区"], df["车辆类型"], normalize="index").to_dict()
    return {"行政区统计": borough_data, "行政区车辆类型占比": borough_company}

@app.get("/api/payment-analysis")
def payment_analysis():
    df = load_and_clean_data()
    payment_map = {1: "信用卡", 2: "现金", 3: "免付费", 4: "争议", 5: "未知", 6: "已作废"}
    df["支付方式名称"] = df["支付方式"].map(payment_map)
    payment_dist = df["支付方式名称"].value_counts().to_dict()
    payment_by_company = {}
    for company in df["车辆类型"].unique():
        company_df = df[df["车辆类型"] == company]
        payment_by_company[company] = company_df["支付方式名称"].value_counts(normalize=True).mul(100).round(2).to_dict()
    avg_tip_by_payment = df.groupby("支付方式名称")["小费"].mean().round(2).to_dict()
    return {"支付方式分布": payment_dist, "车辆类型支付对比": payment_by_company, "各支付方式平均小费": avg_tip_by_payment}

@app.get("/api/time-analysis")
def time_analysis():
    df = load_and_clean_data()
    hourly_avg = []
    for hour in range(24):
        hour_df = df[df["小时"] == hour]
        hourly_avg.append({
            "小时": hour,
            "平均费用": round(hour_df["总费用"].mean(), 2) if len(hour_df) > 0 else 0,
            "平均距离": round(hour_df["行程距离"].mean(), 2) if len(hour_df) > 0 else 0,
            "平均小费": round(hour_df["小费"].mean(), 2) if len(hour_df) > 0 else 0
        })
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday_data = []
    for i, name in enumerate(weekday_names):
        weekday_df = df[df["星期几"] == i]
        weekday_data.append({
            "星期": name,
            "平均费用": round(weekday_df["总费用"].mean(), 2) if len(weekday_df) > 0 else 0,
            "平均距离": round(weekday_df["行程距离"].mean(), 2) if len(weekday_df) > 0 else 0,
            "行程数量": len(weekday_df)
        })
    period_data = []
    for period in df["时段"].unique():
        period_df = df[df["时段"] == period]
        period_data.append({
            "时段": period,
            "平均费用": round(period_df["总费用"].mean(), 2),
            "行程数量": len(period_df)
        })
    return {"小时平均数据": hourly_avg, "星期数据": weekday_data, "时段数据": period_data}

@app.get("/api/zone-hotspots")
def zone_hotspots(top_n: int = Query(10)):
    df = load_and_clean_data()
    top_pu = df["上车区域ID"].value_counts().head(top_n).to_dict()
    top_do = df["下车区域ID"].value_counts().head(top_n).to_dict()
    zone_avg = df.groupby("上车区域ID")["总费用"].mean().sort_values(ascending=False).head(top_n).round(2).to_dict()
    return {"热门上车区域": top_pu, "热门下车区域": top_do, "区域平均费用": zone_avg}

@app.get("/api/correlation-analysis")
def correlation_analysis():
    df = load_and_clean_data()
    numeric_cols = ["行程距离", "车费", "小费", "总费用", "乘客数量", "行程时长_分钟", "小时"]
    existing_cols = [col for col in numeric_cols if col in df.columns]
    corr = df[existing_cols].corr().round(3)
    matrix_data = []
    for col1 in existing_cols:
        for col2 in existing_cols:
            matrix_data.append({"字段1": col1, "字段2": col2, "相关系数": corr.loc[col1, col2]})
    return {"数值字段": existing_cols, "相关性矩阵": matrix_data, "矩阵表格": corr.to_dict()}

@app.get("/api/insights")
def insights():
    df = load_and_clean_data()
    top_tips = df.nlargest(10, "小费")[["车辆类型", "小费", "总费用", "行程距离", "行政区"]].to_dict("records") if "小费" in df.columns else []
    top_distance = df.nlargest(10, "行程距离")[["车辆类型", "行程距离", "总费用", "行政区"]].to_dict("records")
    company_compare = {}
    for company in df["车辆类型"].unique():
        company_df = df[df["车辆类型"] == company]
        company_compare[company] = {
            "平均费用": round(company_df["总费用"].mean(), 2),
            "平均距离": round(company_df["行程距离"].mean(), 2),
            "平均小费": round(company_df["小费"].mean(), 2) if "小费" in df.columns else 0,
            "平均时长": round(company_df["行程时长_分钟"].mean(), 1),
            "行程数量": len(company_df)
        }
    return {"小费Top10": top_tips, "行程距离Top10": top_distance, "车辆类型对比": company_compare}

@app.get("/api/filter-data")
def filter_data(
    车辆类型: str = Query(None),
    最小费用: float = Query(0),
    最大费用: float = Query(1000),
    行政区: str = Query(None),
    起始小时: int = Query(0),
    结束小时: int = Query(23)
):
    df = load_and_clean_data()
    if 车辆类型:
        df = df[df["车辆类型"] == 车辆类型]
    if 最小费用:
        df = df[df["总费用"] >= 最小费用]
    if 最大费用:
        df = df[df["总费用"] <= 最大费用]
    if 行政区:
        df = df[df["行政区"] == 行政区]
    if 起始小时 or 结束小时:
        df = df[(df["小时"] >= 起始小时) & (df["小时"] <= 结束小时)]
    return {
        "筛选后记录数": len(df),
        "平均费用": round(df["总费用"].mean(), 2) if len(df) > 0 else 0,
        "平均距离": round(df["行程距离"].mean(), 2) if len(df) > 0 else 0,
        "车辆类型分布": df["车辆类型"].value_counts().to_dict(),
        "行政区分布": df["行政区"].value_counts().to_dict()
    }

@app.get("/api/raw-data")
def get_raw_data(limit: int = Query(100, le=1000), offset: int = Query(0)):
    df = load_and_clean_data()
    display_cols = ["上车时间", "车辆类型", "行政区", "行程距离", "总费用", "小费", "乘客数量", "支付方式"]
    existing_cols = [col for col in display_cols if col in df.columns]
    result_df = df[existing_cols].iloc[offset:offset+limit]
    payment_map = {1: "信用卡", 2: "现金", 3: "免付费", 4: "争议", 5: "未知", 6: "已作废"}
    if "支付方式" in result_df.columns:
        result_df["支付方式"] = result_df["支付方式"].map(payment_map)
    return {"总记录数": len(df), "当前返回": len(result_df), "数据": result_df.to_dict("records")}

@app.get("/api/dashboard-data")
def dashboard_data():
    df = load_and_clean_data()
    payment_map = {1: "信用卡", 2: "现金", 3: "免付费", 4: "争议", 5: "未知", 6: "已作废"}
    kpi = {
        "总行程数": len(df),
        "总营收(万美元)": round(df['总费用'].sum() / 10000, 1),
        "平均小费率(%)": round(df['小费率'].mean(), 1),
        "平均行程(英里)": round(df['行程距离'].mean(), 1),
        "平均费用($)": round(df['总费用'].mean(), 1),
        "晚高峰占比(%)": round(df['是否晚高峰'].mean() * 100, 1)
    }
    yellow_green_comparison = {
        "平均费用": df.groupby('车辆类型')['总费用'].mean().round(1).to_dict(),
        "平均距离": df.groupby('车辆类型')['行程距离'].mean().round(1).to_dict(),
        "平均小费率": df.groupby('车辆类型')['小费率'].mean().round(1).to_dict(),
        "平均乘客数": df.groupby('车辆类型')['乘客数量'].mean().round(1).to_dict()
    }
    return {
        "kpi": kpi,
        "company_compare": df["车辆类型"].value_counts().to_dict(),
        "hourly_trend": df.groupby('小时').size().to_dict(),
        "weekday_trend": df.groupby('星期几').size().sort_index().to_dict(),
        "borough_dist": df['行政区'].value_counts().to_dict(),
        "period_dist": df['时段'].value_counts().to_dict(),
        "fare_level_dist": df['费用等级'].value_counts().to_dict(),
        "payment_dist": df['支付方式'].map(payment_map).value_counts().to_dict(),
        "passenger_dist": df['乘客数量'].value_counts().sort_index().to_dict(),
        "yellow_green_comparison": yellow_green_comparison,
        "top_pickup_zones": df.groupby('上车区域ID').size().nlargest(10).to_dict(),
        "correlation": df[['行程距离', '车费', '小费', '总费用', '乘客数量', '行程时长_分钟']].corr().round(2).to_dict()
    }

@app.get("/")
def root():
    return {"message": "NYC Taxi API", "endpoints": ["/api/dashboard-data", "/api/filter-data"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
