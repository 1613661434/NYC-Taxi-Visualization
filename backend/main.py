from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import warnings
import os
import glob

warnings.filterwarnings('ignore')

app = FastAPI(title="NYC Taxi API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CONFIG = {
    "clean_data_dir": "../data/clean_data",
    "zone_file_path": "../data/taxi_zone_lookup.csv",
    "sample_size": 50000,
}

df_cache = None

def load_cleaned_data():
    global df_cache
    if df_cache is not None:
        return df_cache

    zone_df = pd.read_csv(CONFIG["zone_file_path"]).rename(columns={"LocationID": "位置ID", "Borough": "行政区"})
    files = glob.glob(os.path.join(CONFIG["clean_data_dir"], "*.parquet"))
    
    df_list = []
    for f in files:
        df_single = pd.read_parquet(f)
        df_single = df_single.sample(min(5000, len(df_single)), random_state=1)
        if "green" in f.lower():
            df_single["车型"] = "绿色出租车"
        elif "yellow" in f.lower():
            df_single["车型"] = "黄色出租车"
        else:
            df_single["车型"] = "未知"
        df_list.append(df_single)
    
    df = pd.concat(df_list, ignore_index=True)
    df = df.sample(min(CONFIG["sample_size"], len(df)), random_state=1)
    
    df = df.merge(zone_df, left_on="上车区域ID", right_on="位置ID", how="left").dropna(subset=["行政区"])
    df["小时"] = df["上车时间"].dt.hour
    df["月份"] = df["上车时间"].dt.month
    df_cache = df
    return df

# 接口：已删除费用参数
@app.get("/api/dashboard-data")
def get_dashboard(
    start_month: int = Query(1, ge=1, le=12),
    end_month: int = Query(12, ge=1, le=12),
    company: str = Query(""),
    borough: str = Query("")
):
    df = load_cleaned_data()
    df = df[(df["月份"] >= start_month) & (df["月份"] <= end_month)]
    
    # 车型 + 行政区筛选
    if company:
        df = df[df["车型"] == company]
    if borough:
        df = df[df["行政区"] == borough]

    if df.empty:
        return {
            "kpi": {"总行程数":0,"总营收(万美元)":0,"平均小费率(%)":0,"平均行程(英里)":0,"平均费用($)":0,"晚高峰占比(%)":0},
            "company_compare":{},"borough_dist":{},"hourly_trend":{},"fare_level_dist":{},"payment_dist":{},
            "weekday_trend":{},"period_dist":{},"passenger_dist":{},"yellow_green_comparison":{},"correlation":{}
        }
    
    return {
        "kpi": {
            "总行程数": len(df),
            "总营收(万美元)": round(df["修正后总费用"].sum() / 10000, 1),
            "平均小费率(%)": round(df["小费"].mean() / df["车费"].mean() * 100, 1) if len(df) else 0,
            "平均行程(英里)": round(df["行程距离"].mean(), 1),
            "平均费用($)": round(df["修正后总费用"].mean(), 1),
            "晚高峰占比(%)": round(len(df[df["小时"].between(17,19)]) / len(df) * 100, 1) if len(df) else 0
        },
        "company_compare": df["车型"].value_counts().to_dict(),
        "borough_dist": df["行政区"].value_counts().to_dict(),
        "hourly_trend": df["小时"].value_counts().sort_index().to_dict(),
        "fare_level_dist": pd.cut(df["修正后总费用"], [0,5,10,20,30,50,1000], labels=["0-5","5-10","10-20","20-30","30-50","50+"]).value_counts().to_dict(),
        "payment_dist": df.get("支付方式", pd.Series([0])).value_counts().to_dict(),
        "weekday_trend": df["上车时间"].dt.weekday.value_counts().sort_index().to_dict(),
        "period_dist": pd.cut(df["小时"], [0,6,10,16,20,24], labels=["深夜","早高峰","白天","晚高峰","夜间"]).value_counts().to_dict(),
        "passenger_dist": df["乘客数量"].value_counts().sort_index().to_dict(),
        "yellow_green_comparison": {
            "平均费用": df.groupby("车型")["修正后总费用"].mean().round(1).to_dict(),
            "平均距离": df.groupby("车型")["行程距离"].mean().round(1).to_dict(),
            "平均小费": df.groupby("车型")["小费"].mean().round(1).to_dict()
        },
        "correlation": df[["行程距离", "车费", "小费", "乘客数量", "修正后总费用"]].corr().round(2).to_dict()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)