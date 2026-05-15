def analyze_missing_values(df):
    results = {
        "columns": [],
        "missing_counts": {},
        "missing_pcts": {},
        "by_taxi_type": {},
        "total_rows": len(df),
    }

    for col in df.columns:
        null_count = int(df[col].isna().sum())
        if null_count > 0:
            results["columns"].append(col)
            results["missing_counts"][col] = null_count
            results["missing_pcts"][col] = round(null_count / len(df) * 100, 2)
            by_type = {}
            for ttype in df["车型"].unique():
                sub = df[df["车型"] == ttype]
                by_type[ttype] = int(sub[col].isna().sum())
            results["by_taxi_type"][col] = by_type

    results["columns"] = sorted(results["columns"], key=lambda c: results["missing_counts"][c], reverse=True)
    return results
