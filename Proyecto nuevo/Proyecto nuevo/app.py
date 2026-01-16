import streamlit as st
import os

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(layout="wide", page_title="DataStrike | Élite Analytics")

# =========================
# IMPORTS
# =========================
from data.loader import load_data
from data.validator import validate
from data.enrich import enrich

from analytics.carriles import perdidas_por_carril
from analytics.jugadores import perdidas_por_jugador
from analytics.kpis import porcentaje_perdidas, kpis_por_periodo
from analytics.zonas import perdidas_zona_carril_periodo
from analytics.efectividad import ganados_vs_perdidos
from analytics.pases import pases_progresivos

from visuals.bars import bar_chart
from visuals.pitch import pitch_map
from visuals.heatmap import heatmap_zona_carril
from visuals.compare import barras_ganados_perdidos
from visuals.heatmap_pitch import heatmap_pitch
from visuals.pases_progresivos import barras_pases_progresivos

from analytics.xg_model import xg_model
from analytics.kpis import total_xg
from visuals.gauge_xg import gauge_xg
import time

# =========================
# CARGA + PREPARACIÓN (CACHE)
# =========================
@st.cache_data(show_spinner=False)
def load_and_prepare(file):
    df = load_data(file)
    df.columns = df.columns.str.strip().str.lower()
    validate(df)
    return enrich(df)

# =========================
# CSS
# =========================
def load_css(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =========================
# TEMA
# =========================

st.set_page_config(layout="wide", page_title="DataStrike | Élite Analytics")

load_css("styles/main.css")

with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding-bottom:20px;'>
            <h1 style='color:#00CC96; font-size:32px; margin:0;'>⚡ DATASTRIKE</h1>
            <p style='color:#8a8d97; font-size:10px; letter-spacing:2px;'>CONTROL CENTER</p>
        </div>
    """, unsafe_allow_html=True)

def animated_gauge(container, start, end, steps=15, delay=0.02):
    delta = (end - start) / steps
    value = start

    for _ in range(steps):
        value += delta
        container.plotly_chart(
            gauge_xg(value),
            use_container_width=True
        )
        time.sleep(delay)
   
# =========================
# UI HELPERS
# =========================
def kpi_card(label, value, icon="📊", status="neutral"):
    color_class = {"good": "kpi-green", "bad": "kpi-red", "warn": "kpi-yellow"}.get(status, "")
    st.markdown(f"""
        <div class="kpi-card {color_class}">
            <div style="display:flex; align-items:center; gap:16px;">
                <div style="font-size:28px;">{icon}</div>
                <div>
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def section(title, subtitle=None):
    sub = f"<div class='section-subtitle'>{subtitle}</div>" if subtitle else ""
    st.markdown(f"""
        <div class="section">
            <div style="border-left:3px solid #00CC96; padding-left:15px;">
                <div class="section-title">{title}</div>
                {sub}
            </div>
    """, unsafe_allow_html=True)

def end_section():
    st.markdown("</div>", unsafe_allow_html=True)

def kpi_delta(label, v1, v2, suffix=""):
    delta = v2 - v1
    st.metric(label, f"{v2:.1f}{suffix}", delta=f"{delta:+.1f}{suffix}")

# =========================
# HEADER PRINCIPAL
# =========================
st.markdown("""
    <div class="main-header-wrapper">
        <h1 class="main-title">DataStrike</h1>
        <div class="main-subtitle-container">
            <div class="subtitle-accent"></div>
            <p class="main-subtitle">ANÁLISIS FUTBOLÍSTICO DE ÉLITE</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# =========================
# CARGA DE ARCHIVO
# =========================
file = st.file_uploader("Cargar CSV / Excel", ["csv", "xlsx"])
if not file:
    st.info("Carga un archivo para comenzar")
    st.stop()

df = load_and_prepare(file)

# =========================
# FILTROS
# =========================
st.sidebar.header("Filtros")


mostrar_heatmap = st.sidebar.checkbox("Mostrar heatmap en cancha", value=False)
mostrar_pases_prog = st.sidebar.checkbox("Mostrar pases progresivos")

periodos = st.sidebar.multiselect("Periodo", sorted(df["periodo"].unique()), default=sorted(df["periodo"].unique()))
jugadores = st.sidebar.multiselect("Jugador", sorted(df["player"].unique()))
eventos = st.sidebar.multiselect("Resultado", sorted(df["event"].unique()))
tipos_evento = st.sidebar.multiselect("Tipo de acción", sorted(df["evento_raw"].dropna().unique()))

df_ctx = df.copy()
if periodos: df_ctx = df_ctx[df_ctx["periodo"].isin(periodos)]
if jugadores: df_ctx = df_ctx[df_ctx["player"].isin(jugadores)]
if eventos: df_ctx = df_ctx[df_ctx["event"].isin(eventos)]
if tipos_evento: df_ctx = df_ctx[df_ctx["evento_raw"].isin(tipos_evento)]

# --- CONTROL EXPLÍCITO DE xG ---
if not tipos_evento:
    df_xg = df_ctx.iloc[0:0]  # DataFrame vacío → xG = 0
else:
    df_xg = xg_model(df_ctx)

# =========================
# KPIs
# =========================
k1, k2, k3 , k4= st.columns(4)
with k1: kpi_card("Eventos", len(df_ctx), "📋", "good")
with k2: kpi_card("Pérdidas", (df_ctx["event"] == "perdida").sum(), "❌", "bad")
with k3: kpi_card("% Pérdidas", f"{porcentaje_perdidas(df_ctx)}%", "📉", "warn")
with k4:
    kpi_card("xG Total", total_xg(df_xg), "⚽", "good")

st.divider()

def animated_gauge(container, start, end, steps=18, delay=0.015):
    if end <= 0:
        container.plotly_chart(gauge_xg(0), use_container_width=True)
        return

    delta = (end - start) / steps
    value = start

    for _ in range(steps):
        value += delta
        container.plotly_chart(
            gauge_xg(value),
            use_container_width=True
        )
        time.sleep(delay)


# =========================
# CARRILES + MAPA
# =========================
section("Distribución y localización", "Pérdidas por carril y eventos")
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(bar_chart(perdidas_por_carril(df_ctx), "carril", "total", "Pérdidas por carril"), use_container_width=True)
with c2:
    st.plotly_chart(heatmap_pitch(df_ctx) if mostrar_heatmap else pitch_map(df_ctx), use_container_width=True)
end_section()

st.divider()

# =========================
# RANKING JUGADORES
# =========================
section("Rendimiento individual", "Pérdidas por jugador")
st.plotly_chart(
    bar_chart(
        perdidas_por_jugador(df_ctx),
        "Jugador",
        "Pérdidas",
        "Pérdidas por jugador"
    ),
    use_container_width=True,
    config={
        "displayModeBar": False,
        "scrollZoom": False,
        "doubleClick": False,
        "staticPlot": True
    }
)


end_section()

st.divider()

# =========================
# KPIs 1T vs 2T
# =========================
st.subheader("KPIs comparativos: 1T vs 2T")
kpis = kpis_por_periodo(df_ctx)
a, b, c = st.columns(3)
with a: kpi_delta("Eventos", kpis["1T"]["total"], kpis["2T"]["total"])
with b: kpi_delta("Pérdidas", kpis["1T"]["perdidas"], kpis["2T"]["perdidas"])
with c: kpi_delta("% Pérdidas", kpis["1T"]["pct_perdidas"], kpis["2T"]["pct_perdidas"], "%")

st.divider()

# =========================
# EFECTIVIDAD
# =========================
section("Efectividad", "Ganados vs Perdidos por periodo")

g1, g2 = st.columns(2)

with g1:
    st.plotly_chart(
        barras_ganados_perdidos(
            ganados_vs_perdidos(df_ctx, "1T"),
            "Ganados vs Perdidos – 1T"
        ),
        use_container_width=True,   # 👈 FALTABA ESTA COMA
        config={
            "displayModeBar": False,
            "scrollZoom": False,
            "doubleClick": False,
            "staticPlot": True
        }
    )

with g2:
    st.plotly_chart(
        barras_ganados_perdidos(
            ganados_vs_perdidos(df_ctx, "2T"),
            "Ganados vs Perdidos – 2T"
        ),
        use_container_width=True,   # 👈 FALTABA ESTA COMA
        config={
            "displayModeBar": False,
            "scrollZoom": False,
            "doubleClick": False,
            "staticPlot": True
        }
        
    )

end_section()

st.divider()

# =========================
# MAPA DE CALOR POR PERIODO
# =========================
section("Mapa de calor de pérdidas", "Comparación espacial 1T vs 2T")

h1, h2 = st.columns(2)

df_1t = perdidas_zona_carril_periodo(df_ctx, "1T")
df_2t = perdidas_zona_carril_periodo(df_ctx, "2T")

with h1:
    st.caption("Primer Tiempo (1T)")
    if not df_1t.empty:
        st.plotly_chart(
            heatmap_zona_carril(df_1t, "Pérdidas 1T"),
            use_container_width=True,   # 👈 FALTABA ESTA COMA
            config={
                "displayModeBar": False,
                "scrollZoom": False,
                "doubleClick": False,
                "staticPlot": True
            }
        )
    else:
        st.info("Sin pérdidas en 1T")

with h2:
    st.caption("Segundo Tiempo (2T)")
    if not df_2t.empty:
        st.plotly_chart(
            heatmap_zona_carril(df_2t, "Pérdidas 2T"),
            use_container_width=True,   # 👈 FALTABA ESTA COMA
            config={
                "displayModeBar": False,
                "scrollZoom": False,
                "doubleClick": False,
                "staticPlot": True
            }
        )
    else:
        st.info("Sin pérdidas en 2T")

end_section()

st.divider()


# =========================
# PASES PROGRESIVOS
# =========================
if mostrar_pases_prog:
    st.divider()
    st.subheader("Análisis de pases progresivos")
    df_prog = pases_progresivos(df_ctx)
    if df_prog.empty:
        st.info("No hay pases progresivos con los filtros actuales")
    else:
        st.plotly_chart(barras_pases_progresivos(df_prog), use_container_width=True, config={
        "displayModeBar": False,
        "scrollZoom": False,
        "doubleClick": False,
        "staticPlot": True
    })
        
st.divider()
section("Expected Goals (xG)", "Modelo exponencial por distancia")

if df_xg.empty:
    st.info("No hay tiros en los filtros actuales")
else:
    xg_total = total_xg(df_xg)

    gauge_container = st.empty()

    animated_gauge(
        gauge_container,
        start=0,
        end=xg_total,
        steps=18,
        delay=0.015
    )

    st.plotly_chart(
        pitch_map(df_xg),
        use_container_width=True
    )

end_section()


