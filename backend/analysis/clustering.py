import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score


def compute_clustering(df, k_range=(2, 8)):
    feature_cols = ["行程距离", "车费", "小费", "乘客数量", "修正后总费用", "小时"]
    available_cols = [c for c in feature_cols if c in df.columns]
    data = df[available_cols].dropna().copy()

    scaler = StandardScaler()
    scaled = scaler.fit_transform(data)

    elbow = []
    silhouette_scores = []
    for k in range(k_range[0], k_range[1] + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(scaled)
        elbow.append({"k": k, "inertia": float(km.inertia_)})
        if k >= 2:
            ss = silhouette_score(scaled, labels)
            silhouette_scores.append({"k": k, "silhouette": round(float(ss), 4)})

    optimal_k = 4
    if len(silhouette_scores) > 0:
        optimal_k = max(silhouette_scores, key=lambda x: x["silhouette"])["k"]

    km_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    labels = km_final.fit_predict(scaled)

    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(scaled)

    scatter_data = []
    sample_n = min(3000, len(pca_result))
    indices = np.random.choice(len(pca_result), sample_n, replace=False)
    for i in indices:
        scatter_data.append({
            "x": round(float(pca_result[i, 0]), 4),
            "y": round(float(pca_result[i, 1]), 4),
            "cluster": int(labels[i]),
        })

    cluster_profiles = []
    for c in range(optimal_k):
        cluster_df = data.iloc[np.where(labels == c)[0]]
        profile = {"cluster": c, "count": len(cluster_df)}
        for col in available_cols:
            profile[col] = round(float(cluster_df[col].mean()), 2)
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
