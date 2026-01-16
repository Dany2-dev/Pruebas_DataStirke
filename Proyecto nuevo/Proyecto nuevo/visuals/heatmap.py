import plotly.express as px

def heatmap_zona_carril(df, titulo):
    return px.density_heatmap(
        df,
        x="carril",
        y="zona",
        z="total",
        color_continuous_scale="Reds",
        title=titulo
    )
