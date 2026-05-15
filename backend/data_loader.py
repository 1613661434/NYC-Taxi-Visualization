import pandas as pd
import glob
import os
from config import CONFIG

df_cache = None
df_full_cache = None
zone_cache = None


def load_zone_lookup():
    global zone_cache
    if zone_cache is not None:
        return zone_cache.copy()
    zone_df = pd.read_csv(CONFIG["zone_file_path"])
    zone_df = zone_df.rename(columns={"LocationID": "位置ID", "Borough": "行政区"})
    zone_cache = zone_df.copy()
    return zone_df


def _build_df(samples_per_file, sample_size):
    """实际从原始文件加载并采样"""
    zone_df = load_zone_lookup()
    files = [f for f in glob.glob(os.path.join(CONFIG["clean_data_dir"], "*.parquet"))
             if not os.path.basename(f).startswith("_")]

    df_list = []
    for f in files:
        df_single = pd.read_parquet(f)
        n = min(samples_per_file, len(df_single))
        df_single = df_single.sample(n, random_state=1)
        if "green" in f.lower():
            df_single["车型"] = "绿色出租车"
        elif "yellow" in f.lower():
            df_single["车型"] = "黄色出租车"
        else:
            df_single["车型"] = "未知"
        df_list.append(df_single)

    df = pd.concat(df_list, ignore_index=True)
    if len(df) > sample_size:
        df = df.sample(sample_size, random_state=1)

    df = df.merge(zone_df, left_on="上车区域ID", right_on="位置ID", how="left").dropna(subset=["行政区"])
    df["小时"] = df["上车时间"].dt.hour
    df["月份"] = df["上车时间"].dt.month

    # 支付方式中文化（兜底 + 数字映射）
    if "支付方式" not in df.columns and "payment_type" in df.columns:
        df["支付方式"] = df["payment_type"]
    if "支付方式" in df.columns:
        payment_labels = {1: "信用卡", 2: "现金", 3: "免收费", 4: "争议", 5: "未知", 6: "无效行程"}
        df["支付方式"] = df["支付方式"].map(payment_labels).fillna("未知")

    return df


def load_cleaned_data(sample_size=None):
    """加载仪表盘数据（优先使用磁盘缓存）"""
    global df_cache

    if sample_size is None and CONFIG["cache_enabled"] and df_cache is not None:
        return df_cache.copy()

    # 尝试从磁盘缓存加载
    disk_path = CONFIG.get("disk_cache_path", "")
    if sample_size is None and disk_path and os.path.exists(disk_path):
        try:
            df = pd.read_parquet(disk_path)
            df_cache = df.copy()
            return df
        except Exception:
            pass

    target = sample_size if sample_size else CONFIG["sample_size"]
    df = _build_df(CONFIG["samples_per_file"], target)

    # 写入磁盘缓存
    if sample_size is None and disk_path:
        try:
            df.to_parquet(disk_path, index=False)
        except Exception:
            pass

    if sample_size is None and CONFIG["cache_enabled"]:
        df_cache = df.copy()

    return df


def load_full_data(sample_size=None):
    """加载分析用数据（内存+磁盘双重缓存）"""
    global df_full_cache

    if sample_size is None and df_full_cache is not None:
        return df_full_cache.copy()

    # 尝试从磁盘缓存加载
    disk_path = CONFIG.get("disk_cache_full_path", "")
    if sample_size is None and disk_path and os.path.exists(disk_path):
        try:
            df = pd.read_parquet(disk_path)
            df_full_cache = df.copy()
            return df
        except Exception:
            pass

    target = sample_size if sample_size else CONFIG["analysis_sample_size"]
    df = _build_df(CONFIG["analysis_per_file"], target)

    # 写入磁盘缓存
    if sample_size is None and disk_path:
        try:
            df.to_parquet(disk_path, index=False)
        except Exception:
            pass

    if sample_size is None:
        df_full_cache = df.copy()

    return df


def apply_filters(df, start_month=1, end_month=12, company="", borough=""):
    df = df[(df["月份"] >= start_month) & (df["月份"] <= end_month)]
    if company:
        df = df[df["车型"] == company]
    if borough:
        df = df[df["行政区"] == borough]
    return df


def clear_cache():
    """清除内存和磁盘缓存（数据更新后调用）"""
    global df_cache
    df_cache = None
    disk_path = CONFIG.get("disk_cache_path", "")
    if disk_path and os.path.exists(disk_path):
        os.remove(disk_path)
