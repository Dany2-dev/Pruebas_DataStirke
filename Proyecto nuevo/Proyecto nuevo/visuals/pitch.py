import plotly.graph_objects as go
import plotly.express as px

PITCH_LENGTH = 105
PITCH_WIDTH = 68


def pitch_map(df):
    # =========================
    # ESCALAR COORDENADAS
    # =========================
    x1 = df["x"] * (PITCH_LENGTH / 100)
    y1 = df["y"] * (PITCH_WIDTH / 100)

    fig = go.Figure()

    # =========================
    # PALETA AUTOMÁTICA DE COLORES
    # =========================
    palette = px.colors.qualitative.Alphabet  # 26 colores únicos

    eventos_unicos = (
        df["evento_raw"]
        .astype(str)
        .str.lower()
        .unique()
    )

    evento_color_map = {
        ev: palette[i % len(palette)]
        for i, ev in enumerate(eventos_unicos)
    }

    def color_evento(row):
        # 🔴 PÉRDIDAS SIEMPRE ROJO
        if row["event"] == "perdida":
            return "#FF4B4B"
        # 🎨 TODO LO DEMÁS (goles, tiros, remates, pases, etc.)
        return evento_color_map.get(
            str(row["evento_raw"]).lower(),
            "#FFFFFF"
        )

    # =========================
    # CANCHA
    # =========================
    line_style = dict(color="rgba(255,255,255,0.3)", width=2)

    shapes = [
        dict(type="rect", x0=0, y0=0, x1=105, y1=68,
             line=line_style, fillcolor="rgba(255,255,255,0.02)"),
        dict(type="line", x0=52.5, y0=0, x1=52.5, y1=68, line=line_style),
        dict(type="circle", x0=43.15, y0=24.15, x1=61.85, y1=42.85, line=line_style),
        dict(type="rect", x0=0, y0=13.84, x1=16.5, y1=54.16, line=line_style),
        dict(type="rect", x0=88.5, y0=13.84, x1=105, y1=54.16, line=line_style),
        dict(type="rect", x0=0, y0=24.84, x1=5.5, y1=43.16, line=line_style),
        dict(type="rect", x0=99.5, y0=24.84, x1=105, y1=43.16, line=line_style),
    ]

    # =========================
    # EVENTOS (PUNTOS)
    # =========================
    fig.add_trace(go.Scatter(
        x=x1,
        y=y1,
        mode="markers",
        marker=dict(
            size=11,
            color=df.apply(color_evento, axis=1),
            line=dict(
                width=1.3,
                color=df.apply(color_evento, axis=1)
            ),
            opacity=0.9
        ),
        text=df["player"].astype(str) + "<br>" + df["evento_raw"].astype(str),
        hoverinfo="text",
        name="Eventos"
    ))

    # =========================
    # PASES / ACCIONES (FLECHAS)
    # =========================
    if {"x2", "y2"}.issubset(df.columns):
        acciones = df[df["x2"].notna() & (df["x2"] != 0)]

        for _, r in acciones.iterrows():
            fig.add_annotation(
                x=r["x2"] * (PITCH_LENGTH / 100),
                y=r["y2"] * (PITCH_WIDTH / 100),
                ax=r["x"] * (PITCH_LENGTH / 100),
                ay=r["y"] * (PITCH_WIDTH / 100),
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1.3,
                arrowcolor=color_evento(r),
                opacity=0.55
            )

    # =========================
    # LAYOUT FINAL
    # =========================
    fig.update_layout(
        shapes=shapes,
        xaxis=dict(range=[-5, 110], visible=False, fixedrange=True),
        yaxis=dict(range=[-5, 73], visible=False, fixedrange=True,
                   scaleanchor="x", scaleratio=1),
        margin=dict(l=0, r=0, t=0, b=0),
        height=500,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )

    return fig
