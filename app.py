import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulasi Hukum Ohm Dinamis", layout="wide")

# =========================
# UTILITAS
# =========================
def clamp(x, low, high):
    return max(low, min(x, high))

def norm(x, xmin, xmax):
    if xmax == xmin:
        return 0
    return (x - xmin) / (xmax - xmin)

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def lerp_color(c1, c2, t):
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return rgb_to_hex((r, g, b))

def resistor_color(r_norm):
    # hijau -> kuning -> merah
    if r_norm <= 0.5:
        return lerp_color("#16a34a", "#f59e0b", r_norm / 0.5)
    else:
        return lerp_color("#f59e0b", "#dc2626", (r_norm - 0.5) / 0.5)

# =========================
# SVG DINAMIS
# =========================
def build_svg(V, R, I):
    v_norm = norm(V, 0, 24)
    r_norm = norm(R, 1, 20)
    i_norm = clamp(I / 10, 0, 1)  # dibatasi agar visual tetap proporsional

    # baterai
    battery_h = 120 + 120 * v_norm
    battery_w = 50 + 24 * v_norm
    battery_font = 20 + 20 * v_norm
    battery_bottom = 330
    battery_top = battery_bottom - battery_h
    battery_x = 200 - battery_w / 2
    battery_cap_w = battery_w * 0.35
    battery_cap_h = 12

    # resistor
    resistor_len = 120 + 120 * r_norm
    resistor_amp = 12 + 22 * r_norm
    resistor_font = 20 + 20 * r_norm
    resistor_x = 470
    resistor_y = 140
    res_color = resistor_color(r_norm)

    # arus
    arrow_len = 160 + 260 * i_norm
    arrow_end = min(250 + arrow_len, 760)
    arrow_thickness = 3 + 3 * i_norm
    current_font = 20 + 18 * i_norm
    anim_dur = max(1.2, 7.0 - min(I, 12) * 0.4)

    # persamaan
    eq_v = 34 + 26 * v_norm
    eq_i = 34 + 26 * i_norm
    eq_r = 34 + 26 * r_norm

    # titik zigzag resistor
    pts = [(resistor_x, resistor_y)]
    segments = 10
    for k in range(1, segments):
        x = resistor_x + (resistor_len / segments) * k
        y = resistor_y - resistor_amp if k % 2 else resistor_y + resistor_amp
        pts.append((x, y))
    pts.append((resistor_x + resistor_len, resistor_y))
    zigzag = " ".join(f"{x},{y}" for x, y in pts)

    svg = f"""
    <svg width="100%" viewBox="0 0 980 700" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="arrowHead" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
          <path d="M0,0 L12,6 L0,12 z" fill="#2563eb"></path>
        </marker>
        <linearGradient id="batteryGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#fbbf24"/>
          <stop offset="100%" stop-color="#f97316"/>
        </linearGradient>
      </defs>

      <rect x="10" y="10" width="960" height="680" rx="22" fill="#ffffff" stroke="#d1d5db" stroke-width="2"></rect>

      <text x="35" y="45" font-size="28" font-weight="700" fill="#111827">
        Simulasi Hukum Ohm Dinamis
      </text>
      <text x="35" y="72" font-size="16" fill="#4b5563">
        Geser slider untuk melihat perubahan visual baterai, resistor, persamaan, dan arus.
      </text>

      <!-- JALUR ARUS ATAS -->
      <path id="currentPath" d="M 250 105 L 760 105" fill="none" stroke="none"></path>

      <!-- PANAH ARUS -->
      <line x1="250" y1="105" x2="{arrow_end}" y2="105"
            stroke="#2563eb" stroke-width="{arrow_thickness}" marker-end="url(#arrowHead)"></line>

      <!-- TITIK-TITIK ARUS BERGERAK -->
      <circle cx="0" cy="0" r="5" fill="#2563eb">
        <animateMotion dur="{anim_dur}s" repeatCount="indefinite">
          <mpath href="#currentPath"></mpath>
        </animateMotion>
      </circle>
      <circle cx="0" cy="0" r="5" fill="#3b82f6">
        <animateMotion dur="{anim_dur}s" begin="-1.8s" repeatCount="indefinite">
          <mpath href="#currentPath"></mpath>
        </animateMotion>
      </circle>
      <circle cx="0" cy="0" r="5" fill="#60a5fa">
        <animateMotion dur="{anim_dur}s" begin="-3.2s" repeatCount="indefinite">
          <mpath href="#currentPath"></mpath>
        </animateMotion>
      </circle>

      <text x="505" y="85" text-anchor="middle" font-size="{current_font}" font-weight="800" fill="#ea580c">
        I = {I:.2f} A
      </text>

      <!-- KABEL -->
      <!-- atas kiri -->
      <line x1="200" y1="140" x2="470" y2="140" stroke="#111827" stroke-width="5"></line>

      <!-- resistor di jalur atas -->
      <polyline points="{zigzag}" fill="none" stroke="{res_color}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"></polyline>

      <!-- atas kanan -->
      <line x1="{resistor_x + resistor_len}" y1="140" x2="800" y2="140" stroke="#111827" stroke-width="5"></line>

      <!-- kanan -->
      <line x1="800" y1="140" x2="800" y2="380" stroke="#111827" stroke-width="5"></line>

      <!-- bawah -->
      <line x1="800" y1="380" x2="200" y2="380" stroke="#111827" stroke-width="5"></line>

      <!-- kiri atas (kabel ke baterai) -->
      <line x1="200" y1="140" x2="200" y2="{battery_top}" stroke="#111827" stroke-width="5"></line>

      <!-- kiri bawah (kabel dari baterai) -->
      <line x1="200" y1="{battery_bottom}" x2="200" y2="380" stroke="#111827" stroke-width="5"></line>

      <!-- baterai -->
      <rect x="{battery_x}" y="{battery_top}" width="{battery_w}" height="{battery_h}" rx="10"
            fill="url(#batteryGrad)" stroke="#92400e" stroke-width="2"></rect>
      <rect x="{battery_x}" y="{battery_top + battery_h * 0.58}" width="{battery_w}" height="{battery_h * 0.42}"
            fill="#1f2937"></rect>
      <rect x="{200 - battery_cap_w/2}" y="{battery_top - battery_cap_h}" width="{battery_cap_w}" height="{battery_cap_h}"
            rx="3" fill="#9ca3af"></rect>

      <text x="200" y="{battery_top + battery_h * 0.28}" text-anchor="middle"
            font-size="{battery_font}" font-weight="700" fill="white">+</text>
      <text x="200" y="{battery_top + battery_h * 0.86}" text-anchor="middle"
            font-size="{battery_font}" font-weight="700" fill="white">−</text>

      <text x="{battery_x - 20}" y="{battery_top - 18}" font-size="{battery_font}" font-weight="800" fill="#2563eb">
        V = {V:.2f} V
      </text>

      <!-- label resistor -->
      <text x="{resistor_x + resistor_len/2}" y="{resistor_y + resistor_amp + 48}" text-anchor="middle"
            font-size="{resistor_font}" font-weight="800" fill="{res_color}">
        R = {R:.2f} Ω
      </text>

      <!-- PANEL PERSAMAAN -->
      <rect x="60" y="450" width="400" height="180" rx="18" fill="#f8fafc" stroke="#cbd5e1"></rect>
      <text x="85" y="485" font-size="24" font-weight="700" fill="#111827">Persamaan Dinamis</text>

      <text x="105" y="550" font-size="{eq_v}" font-weight="900" fill="#2563eb">V</text>
      <text x="165" y="550" font-size="40" font-weight="800" fill="#111827">=</text>
      <text x="220" y="550" font-size="{eq_i}" font-weight="900" fill="#ea580c">I</text>
      <text x="275" y="550" font-size="{eq_r}" font-weight="900" fill="{res_color}">R</text>

      <text x="85" y="600" font-size="22" fill="#374151">
        {V:.2f} = {I:.2f} × {R:.2f}
      </text>

      <!-- PANEL INTERPRETASI -->
      <rect x="500" y="450" width="400" height="180" rx="18" fill="#fff7ed" stroke="#fed7aa"></rect>
      <text x="525" y="485" font-size="24" font-weight="700" fill="#9a3412">Interpretasi</text>
      <text x="525" y="525" font-size="20" fill="#7c2d12">• Tegangan naik → baterai membesar</text>
      <text x="525" y="555" font-size="20" fill="#7c2d12">• Hambatan naik → resistor membesar & berubah warna</text>
      <text x="525" y="585" font-size="20" fill="#7c2d12">• Arus ditunjukkan oleh panah dan titik-titik bergerak</text>
      <text x="525" y="615" font-size="20" fill="#7c2d12">• Nilai arus saat ini = {I:.2f} A</text>
    </svg>
    """
    return svg

# =========================
# HEADER
# =========================
st.title("Simulasi Hukum Ohm")
st.write(
    "Versi ini menampilkan rangkaian dinamis: ukuran baterai mengikuti tegangan, "
    "ukuran dan warna resistor mengikuti hambatan, serta pembacaan arus divisualkan "
    "dengan panah dan animasi."
)

# =========================
# INPUT
# =========================
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Parameter")
    V = st.slider("Tegangan (V)", 0.0, 24.0, 12.0, 0.5)
    R = st.slider("Hambatan (Ω)", 1.0, 20.0, 6.0, 0.5)
    I = V / R

    st.metric("Tegangan", f"{V:.2f} V")
    st.metric("Hambatan", f"{R:.2f} Ω")
    st.metric("Arus", f"{I:.2f} A")

    st.markdown("### Penjelasan")
    st.write("Jika tegangan diperbesar pada hambatan tetap, maka arus bertambah.")
    st.write("Jika hambatan diperbesar pada tegangan tetap, maka arus berkurang.")

with col2:
    st.subheader("Visualisasi Dinamis")
    components.html(build_svg(V, R, I), height=720, scrolling=False)

# =========================
# TABEL DATA
# =========================
st.subheader("Tabel Nilai")
voltages = np.arange(0, 25, 2)
currents = voltages / R

df = pd.DataFrame({
    "Tegangan (V)": voltages,
    "Hambatan (Ω)": [R] * len(voltages),
    "Arus (A)": np.round(currents, 3)
})
st.dataframe(df, use_container_width=True)

# =========================
# GRAFIK
# =========================
st.subheader("Grafik Arus terhadap Tegangan")
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(voltages, currents, marker="o")
ax.set_xlabel("Tegangan (V)")
ax.set_ylabel("Arus (A)")
ax.set_title(f"Hubungan I terhadap V pada R = {R:.2f} Ω")
ax.grid(True)
st.pyplot(fig)

# =========================
# RINGKASAN
# =========================
st.subheader("Pembacaan Dinamis")
st.write(
    f"Pada pengaturan saat ini, tegangan = {V:.2f} V, hambatan = {R:.2f} Ω, "
    f"sehingga arus yang mengalir adalah {I:.2f} A."
)
