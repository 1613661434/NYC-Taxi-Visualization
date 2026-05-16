import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score


def compute_clustering(df, k_range=(2, 6)):
    feature_cols = ["行程距离", "车费", "小费", "乘客数量", "修正后总费用", "小时"]
    available_cols = [c for c in feature_cols if c in df.columns]
    data = df[available_cols].dropna().copy()

    scaler = StandardScaler()
    scaled = scaler.fit_transform(data)

    # 对大数据集采样用于 KMeans 训练，加速但不影响结果有效性
    train_n = min(8000, len(scaled))
    if len(scaled) > train_n:
        train_idx = np.random.choice(len(scaled), train_n, replace=False)
        scaled_train = scaled[train_idx]
    else:
        scaled_train = scaled

    elbow = []
    silhouette_scores = []
    for k in range(k_range[0], k_range[1] + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init=5)
        labels_train = km.fit_predict(scaled_train)
        elbow.append({"k": k, "inertia": float(km.inertia_)})
        if k >= 2:
            # silhouette 采样计算：O(sample_size²) 替代 O(N²)，大幅加速
            ss = silhouette_score(scaled_train, labels_train, sample_size=3000, random_state=42)
            silhouette_scores.append({"k": k, "silhouette": round(float(ss), 4)})

    optimal_k = 4
    if len(silhouette_scores) > 0:
        optimal_k = max(silhouette_scores, key=lambda x: x["silhouette"])["k"]

    # 在 10K 采样上训练最终模型，然后 O(N) 预测全量标签（避免 O(N·K·I) 的 fit_predict）
    final_train_n = min(10000, len(scaled))
    final_idx = np.random.choice(len(scaled), final_train_n, replace=False)
    km_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=3)
    km_final.fit(scaled[final_idx])
    labels = km_final.predict(scaled)

    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(scaled)

    scatter_data = []
    sample_n = min(1500, len(pca_result))
    indices = np.random.choice(len(pca_result), sample_n, replace=False)
    for i in indices:
        scatter_data.append({
            "x": round(float(pca_result[i, 0]), 4),
            "y": round(float(pca_result[i, 1]), 4),
            "cluster": int(labels[i]),
        })

    cluster_profiles = []
    global_means = {col: float(data[col].mean()) for col in available_cols}
    for c in range(optimal_k):
        cluster_df = data.iloc[np.where(labels == c)[0]]
        profile = {"cluster": c, "count": len(cluster_df)}
        for col in available_cols:
            profile[col] = round(float(cluster_df[col].mean()), 2)

        # 自动生成聚类标签
        tags = []
        dist = profile.get("行程距离", 0)
        fare = profile.get("修正后总费用", 0)
        tip = profile.get("小费", 0)
        hour = profile.get("小时", 0)
        passengers = profile.get("乘客数量", 0)

        g_dist = global_means.get("行程距离", 1)
        g_fare = global_means.get("修正后总费用", 1)
        g_tip = global_means.get("小费", 1)
        g_passengers = global_means.get("乘客数量", 1)

        if dist > g_dist * 1.5 and fare > g_fare * 1.5:
            tags.append("长途高消费")
        elif dist < g_dist * 0.5 and fare < g_fare * 0.5:
            tags.append("短途经济")

        tip_rate = tip / fare if fare > 0 else 0
        g_tip_rate = g_tip / g_fare if g_fare > 0 else 0
        if tip_rate > g_tip_rate * 1.3:
            tags.append("高小费")

        if 6 <= hour <= 9:
            tags.append("早高峰")
        elif 17 <= hour <= 19:
            tags.append("晚高峰")
        elif 22 <= hour or hour <= 5:
            tags.append("深夜出行")

        if passengers > g_passengers * 1.3:
            tags.append("多人拼车")

        if not tags:
            if fare > g_fare:
                tags.append("普通偏高消费")
            else:
                tags.append("普通经济型")

        profile["label"] = " · ".join(tags)
        cluster_profiles.append(profile)

    return {
        "elbow": elbow,
        "silhouette": silhouette_scores,
        "optimal_k": optimal_k,
        "scatter_data": scatter_data,
        "cluster_profiles": cluster_profiles,
        "pca_variance": [round(float(v), 4) for v in pca.explained_variance_ratio_],
        "features_used": available_cols,
    }
