import plotly.graph_objects as go

def gauge_xg(valor, max_val=0.6):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        number=dict(
            suffix="%",
            font=dict(size=28)
        ),
        gauge=dict(
            axis=dict(
                range=[0, max_val],
                tickwidth=1,
                tickcolor="white"
            ),
            bar=dict(color="#E63946"),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            steps=[
                dict(range=[0, max_val*0.4], color="#FFD166"),
                dict(range=[max_val*0.4, max_val*0.7], color="#FCA311"),
                dict(range=[max_val*0.7, max_val], color="#E63946"),
            ],
            threshold=dict(
                line=dict(color="#1f77b4", width=3),
                thickness=0.75,
                value=valor
            )
        ),
        domain={"x": [0, 1], "y": [0, 1]}
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    return fig
