import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error


def train_prediction_model(df):
    feature_cols = ["行程距离", "乘客数量", "小时", "月份"]
    avail = [c for c in feature_cols if c in df.columns]
    data = df[avail + ["车费"]].dropna().copy()

    X = data[avail]
    y = data["车费"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    r2 = float(r2_score(y_test, y_pred))
    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))

    coefficients = []
    for name, coef in zip(avail, model.coef_):
        coefficients.append({"feature": name, "coefficient": round(float(coef), 4)})
    coefficients.sort(key=lambda x: abs(x["coefficient"]), reverse=True)

    residuals = y_test.values - y_pred
    residual_hist = np.histogram(residuals, bins=20)
    residual_dist = [
        {"bin_start": round(float(residual_hist[1][i]), 2), "count": int(residual_hist[0][i])}
        for i in range(len(residual_hist[0]))
    ]

    sample_n = min(500, len(y_test))
    indices = np.random.choice(len(y_test), sample_n, replace=False)
    predictions = []
    for i in indices:
        predictions.append({
            "actual": round(float(y_test.values[i]), 2),
            "predicted": round(float(y_pred[i]), 2),
            "residual": round(float(residuals[i]), 2),
        })

    return {
        "coefficients": coefficients,
        "metrics": {"r2": round(r2, 4), "mae": round(mae, 2), "rmse": round(rmse, 2)},
        "predictions": predictions,
        "residual_distribution": residual_dist,
        "intercept": round(float(model.intercept_), 4),
    }
