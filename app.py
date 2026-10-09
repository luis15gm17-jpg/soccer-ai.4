import streamlit as st
import math

st.set_page_config(page_title="Soccer AI", page_icon="⚽", layout="wide")
st.title("⚽ Soccer AI — Analizador de partidos")
st.caption("Prototipo estadístico: no garantiza resultados ni consulta datos deportivos en vivo.")

def pois(k, lam):
    return math.exp(-lam) * lam**k / math.factorial(k)

def fair(p):
    return 1 / p if p > 0 else float("inf")

def predict(lh, la, cap=10):
    p1 = px = p2 = over25 = btts = 0.0
    scores = []
    for h in range(cap + 1):
        for a in range(cap + 1):
            p = pois(h, lh) * pois(a, la)
            scores.append((p, h, a))
            if h > a: p1 += p
            elif h == a: px += p
            else: p2 += p
            if h + a >= 3: over25 += p
            if h >= 1 and a >= 1: btts += p
    return p1, px, p2, over25, 1-over25, btts, sorted(scores, reverse=True)[:5]

with st.sidebar:
    st.header("Partido")
    home = st.text_input("Equipo local", "Bayern Munich")
    away = st.text_input("Equipo visitante", "Borussia Dortmund")
    league = st.text_input("Liga", "Bundesliga")
    st.subheader("Promedios estimados")
    st.caption("Introduce promedios recientes comparables.")
    xg_h = st.number_input("xG local", 0.1, 5.0, 1.8, 0.1)
    xga_h = st.number_input("xGA local", 0.1, 5.0, 1.1, 0.1)
    xg_a = st.number_input("xG visitante", 0.1, 5.0, 1.4, 0.1)
    xga_a = st.number_input("xGA visitante", 0.1, 5.0, 1.3, 0.1)
    st.subheader("Cuotas opcionales")
    odd1 = st.number_input("Cuota local", 1.01, 100.0, 1.80, 0.01)
    oddx = st.number_input("Cuota empate", 1.01, 100.0, 3.70, 0.01)
    odd2 = st.number_input("Cuota visitante", 1.01, 100.0, 4.20, 0.01)

lh = max(0.15, min(4.5, 0.55*xg_h + 0.45*xga_a + 0.15))
la = max(0.15, min(4.5, 0.55*xg_a + 0.45*xga_h))
p1, px, p2, over, under, btts, scores = predict(lh, la)

st.subheader(f"{home} vs {away}")
st.write(f"Liga: **{league}**")
c1, c2, c3 = st.columns(3)
c1.metric("xG estimado local", f"{lh:.2f}")
c2.metric("xG estimado visitante", f"{la:.2f}")
c3.metric("Total esperado", f"{lh+la:.2f}")

st.subheader("Probabilidades estimadas")
cols = st.columns(6)
for col, name, p in zip(cols, ["1 Local", "X Empate", "2 Visitante", "Más 2.5", "Menos 2.5", "Ambos marcan"],
                         [p1, px, p2, over, under, btts]):
    col.metric(name, f"{p*100:.1f}%", f"Cuota justa {fair(p):.2f}")

st.subheader("Valor teórico frente a cuotas")
rows = []
for name, p, odds in [("Local", p1, odd1), ("Empate", px, oddx), ("Visitante", p2, odd2)]:
    rows.append({"Mercado": name, "Probabilidad": f"{p*100:.1f}%", "Cuota ingresada": f"{odds:.2f}",
                 "Cuota justa": f"{fair(p):.2f}", "EV teórico": f"{(p*odds-1)*100:+.1f}%"})
st.dataframe(rows, use_container_width=True, hide_index=True)

st.subheader("Marcadores más probables")
for p, h, a in scores:
    st.write(f"**{h} - {a}** · {p*100:.2f}%")

st.info("Esta primera versión no descarga datos actuales ni incluye alineaciones, lesiones, tiros a puerta, corners o cuotas automáticas. Para eso falta conectar fuentes de datos y validar el modelo con partidos históricos.")
st.caption("Es una estimación, no una garantía de ganancia.")
