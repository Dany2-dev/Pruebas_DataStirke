import numpy as np

GOAL_X = 105
GOAL_Y = 34

def xg_model(df, a=0.45, b=0.02, k=18):

    shots = df[
        df["evento_raw"]
        .astype(str)
        .str.lower()
        .str.contains("tiro|remate|shot|gol")
    ].copy()

    if shots.empty:
        return shots

    shots["distance"] = np.sqrt(
        (shots["x"] - GOAL_X) ** 2 +
        (shots["y"] - GOAL_Y) ** 2
    )

    shots["xG"] = np.exp(-shots["distance"] / k) * a + b

    return shots
