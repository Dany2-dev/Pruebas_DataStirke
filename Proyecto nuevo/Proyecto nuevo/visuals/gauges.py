import plotly.graph_objects as go

def gauge(valor, titulo):
    return go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        title={"text": titulo},
        gauge={"axis": {"range": [0,100]}}
    ))
