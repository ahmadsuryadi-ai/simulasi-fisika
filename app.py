import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulasi Hukum Ohm Dinamis", layout="wide")

st.title("Simulasi Hukum Ohm Dinamis")
st.write("Geser slider untuk melihat perubahan visual pada baterai, resistor, persamaan, dan arus dalam rangkaian.")

# =========================
# INPUT
# =========================
left, right = st.columns([1, 2])

with left:
    st.subheader("Parameter")
    V = st.slider("Tegangan V (Volt)", 0.0, 24.0, 12.0, 0.5)
    R = st.slider("Hambatan R (Ohm)", 1.0, 20.0, 6.0, 0.5)
    I = V / R

    st.metric("Tegangan", f"{V:.2f} V")
    st.metric("Hambatan", f"{R:.2f} Ω")
    st.metric("Arus", f"{I:.2f} A")

    st.info("Rumus dasar: V = I × R")

# =========================
# FUNGSI SVG DINAMIS
# =========================
def draw_dynamic_circuit(V, R, I):
    # Skala visual baterai
    battery_h = 90 + (V / 24.0) * 120
    battery_w = 36 + (V / 24.0) * 28
    battery_font = 16 + (V / 24.0) * 22

    # Skala visual resistor
    resistor_w = 70 + (R / 20.0) * 120
    resistor_h = 30 + (R / 20.0) * 34
    resistor_font = 16 + (R / 20.0) * 22

    # Skala visual arus
    arrow_len = 60 + min(I, 6) * 45
    arrow_thickness = 2 + min(I, 6) * 1.5
    current_font = 16 + min(I, 6) * 4

    # Skala persamaan
    eq_font_v = 28 + (V / 24.0) * 24
    eq_font_r = 28 + (R / 20.0) * 24
    eq_font_i = 28 + min(I, 6) * 8

    # Posisi
    x0, y0 = 90, 100
    x1, y1 = 620, 100
    x2, y2 = 620, 330
    x3, y3 = 90, 330

    battery_x = 120
    battery_y = 160

    resistor_x = 470
    resistor_y = 205

    # Zigzag resistor path
    rw = resistor_w
    rh = resistor_h
    rx = resistor_x
    ry = resistor_y

    zigzag_points = [
        (rx, ry),
        (rx + rw*0.10, ry - rh/2),
        (rx + rw*0.20, ry + rh/2),
        (rx + rw*0.30, ry - rh/2),
        (rx + rw*0.40, ry + rh/2),
        (rx + rw*0.50, ry - rh/2),
        (rx + rw*0.60, ry + rh/2),
        (rx + rw*0.70, ry - rh/2),
        (rx + rw*0.80, ry + rh/2),
        (rx + rw*0.90, ry - rh/2),
        (rx + rw, ry),
    ]
    zigzag_str = " ".join([f"{x},{y}" for x, y in zigzag_points])

    svg = f"""
    <svg width="100%" viewBox="0 0 900 560" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="arrowHead" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
          <path d="M0,0 L12,6 L0,12 z" fill="#2563eb"></path>
        </marker>
        <linearGradient id="batteryFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#f59e0b"/>
          <stop offset="100%" stop-color="#f97316"/>
        </linearGradient>
      </defs>

      <rect x="20" y="20" width="860" height="520" rx="22" fill="#ffffff" stroke="#d1d5db" stroke-width="2"/>

      <text x="40" y="60" font-size="28" font-weight="700" fill="#111827">Rangkaian Dinamis Hukum Ohm</text>

      <!-- kabel -->
      <line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="#111827" stroke-width="5"/>
      <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#111827" stroke-width="5"/>
      <line x1="{x2}" y1="{y2}" x2="{x3}" y2="{y3}" stroke="#111827" stroke-width="5"/>
      <line x1="{x3}" y1="{y3}" x2="{x0}" y2="{y0}" stroke="#111827" stroke-width="5"/>

      <!-- baterai -->
      <rect x="{battery_x}" y="{battery_y}" width="{battery_w}" height="{battery_h}" rx="10" fill="url(#batteryFill)" stroke="#92400e" stroke-width="2"/>
      <rect x="{battery_x}" y="{battery_y + battery_h*0.58}" width="{battery_w}" height="{battery_h*0.42}" rx="0" fill="#1f2937"/>
      <text x="{battery_x + battery_w/2}" y="{battery_y + battery_h*0.28}" text-anchor="middle"
            font-size="{battery_font}" font-weight="700" fill="white">+</text>
      <text x="{battery_x + battery_w/2}" y="{battery_y + battery_h*0.85}" text-anchor="middle"
            font-size="{battery_font}" font-weight="700" fill="white">−</text>

      <text x="{battery_x - 20}" y="{battery_y - 24}" font-size="{battery_font}" font-weight="700" fill="#2563eb">
        V = {V:.2f} V
      </text>

      <!-- resistor -->
      <line x1="620" y1="180" x2="{rx}" y2="180" stroke="#111827" stroke-width="5"/>
      <line x1="{rx + rw}" y1="180" x2="620" y2="180" stroke="#111827" stroke-width="5"/>
      <polyline points="{zigzag_str}" fill="none" stroke="#dc2626" stroke-width="4"/>
      <text x="{rx + rw/2}" y="{ry + rh + 40}" text-anchor="middle"
            font-size="{resistor_font}" font-weight="700" fill="#16a34a">
        R = {R:.2f} Ω
      </text>

      <!-- panah arus -->
      <line x1="230" y1="78" x2="{230 + arrow_len}" y2="78"
            stroke="#2563eb" stroke-width="{arrow_thickness}" marker-end="url(#arrowHead)"/>
      <text x="{250 + arrow_len/2}" y="56" text-anchor="middle"
            font-size="{current_font}" font-weight="700" fill="#ea580c">
        I = {I:.2f} A
      </text>

      <!-- persamaan dinamis -->
      <text x="690" y="170" font-size="24" font-weight="700" fill="#111827">Persamaan:</text>
      <text x="690" y="235" font-size="{eq_font_v}" font-weight="800" fill="#2563eb">V</text>
      <text x="735" y="235" font-size="34" font-weight="700" fill="#111827">=</text>
      <text x="775" y="235" font-size="{eq_font_i}" font-weight="800" fill="#ea580c">I</text>
      <text x="815" y="235" font-size="{eq_font_r}" font-weight="800" fill="#16a34a">R</text>

      <!-- keterangan -->
      <rect x="650" y="290" width="190" height="160" rx="16" fill="#f8fafc" stroke="#cbd5e1"/>
      <text x="670" y="325" font-size="20" font-weight="700" fill="#111827">Interpretasi</text>
      <text x="670" y="360" font-size="18" fill="#374151">Jika V naik, I naik</text>
      <text x="670" y="392" font-size="18" fill="#374151">Jika R naik, I turun</text>
      <text x="670" y="424" font-size="18" fill="#374151">Arah arus ditunjukkan</text>
      <text x="670" y="448" font-size="18" fill="#374151">oleh panah biru</text>
    </svg>
    """
    return svg

with right:
    st.subheader("Visualisasi Dinamis")
    st.markdown(draw_dynamic_circuit(V, R, I), unsafe_allow_html=True)

# =========================
# DATA DAN GRAFIK
# =========================
st.subheader("Tabel Nilai")
voltages = np.arange(0, 25, 3)
currents = voltages / R
df = pd.DataFrame({
    "Tegangan (V)": voltages,
    "Hambatan (Ω)": [R] * len(voltages),
    "Arus (A)": np.round(currents, 3)
})
st.dataframe(df, use_container_width=True)

st.subheader("Grafik Arus terhadap Tegangan")
fig, ax = plt.subplots()
ax.plot(voltages, currents, marker="o")
ax.set_xlabel("Tegangan (V)")
ax.set_ylabel("Arus (A)")
ax.set_title(f"I terhadap V pada R = {R:.2f} Ω")
ax.grid(True)
st.pyplot(fig)

st.subheader("Pembacaan Dinamis")
st.write(
    f"Pada saat ini, tegangan bernilai {V:.2f} V, hambatan bernilai {R:.2f} Ω, "
    f"dan arus yang terbaca adalah {I:.2f} A."
)
