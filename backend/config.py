CONFIG = {
    "clean_data_dir": "../data/clean_data",
    "zone_file_path": "../data/taxi_zone_lookup.csv",
    # 采样量：大幅减小以降低计算压力
    "sample_size": 15000,
    "samples_per_file": 600,
    "analysis_sample_size": 20000,   # 分析用也减小
    "analysis_per_file": 1000,
    "cache_enabled": True,
    "disk_cache_path": "../data/clean_data/_cached_sample.parquet",
    "disk_cache_full_path": "../data/clean_data/_cached_full.parquet",
}
