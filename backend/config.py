CONFIG = {
    "clean_data_dir": "../data/clean_data",
    "zone_file_path": "../data/taxi_zone_lookup.csv",
    # 采样比例：每个文件随机抽取10%
    "sample_ratio": 0.1,
    "sample_size": 50000,          # 仪表盘最终采样上限
    "analysis_sample_size": 100000,  # 分析用最终采样上限
    "cache_enabled": True,
    "disk_cache_path": "../data/clean_data/_cached_sample.parquet",
    "disk_cache_full_path": "../data/clean_data/_cached_full.parquet",
}
