import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Simulasi Hukum Ohm Interaktif",
    page_icon="⚡",
    layout="wide"
)

# =========================
# SESSION STATE
# =========================
if "records" not in st.session_state:
    st.session_state.records = []

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# =========================
# STYLE
# =========================
st.markdown("""
<style>
.block-container {
    padding-top: 1.1rem;
    padding-bottom: 1.5rem;
    max-width: 1400px;
}
.metric-card {
    background: linear-gradient(135deg, #ffffff, #f8fafc);
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}
.metric-label {
    font-size: 0.95rem;
    color: #6b7280;
    margin-bottom: 6px;
}
.metric-blue {
    font-size: 2rem;
    font-weight: 800;
    color: #2563eb;
}
.metric-green {
    font-size: 2rem;
    font-weight: 800;
    color: #16a34a;
}
.metric-orange {
    font-size: 2rem;
    font-weight: 800;
    color: #ea580c;
}
.panel-box {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.04);
}
.title-main {
    font-size: 2rem;
    font-weight: 800;
    color: #111827;
    margin-bottom: 0.2rem;
}
.subtitle-main {
    color: #4b5563;
    font-size: 1rem;
    margin-bottom: 1rem;
}
.note-text {
    color: #6b7280;
    font-size: 0.92rem;
}
</style>
""", unsafe_allow_html=True)

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
    if r_norm <= 0.5:
        return lerp_color("#16a34a", "#f59e0b", r_norm / 0.5)
    return lerp_color("#f59e0b", "#dc2626", (r_norm - 0.5) / 0.5)

# =========================
# SVG RANGKAIAN
# =========================
def build_svg(V, R, I):
    v_norm = norm(V, 0, 24)
    r_norm = norm(R, 1, 20)
    i_norm = clamp(I / 10, 0, 1)

    battery_h = 120 + 120 * v_norm
    battery_w = 50 + 24 * v_norm
    battery_font = 20 + 20 * v_norm
    battery_bottom = 330
    battery_top = battery_bottom - battery_h
    battery_x = 200 - battery_w / 2
    battery_cap_w = battery_w * 0.35
    battery_cap_h = 12

    resistor_len = 120 + 120 * r_norm
    resistor_amp = 12 + 22 * r_norm
    resistor_font = 20 + 20 * r_norm
    resistor_x = 470
    resistor_y = 140
    res_color = resistor_color(r_norm)

    arrow_len = 160 + 260 * i_norm
    arrow_end = min(250 + arrow_len, 760)
    arrow_thickness = 3 + 3 * i_norm
    current_font = 20 + 18 * i_norm
    anim_dur = max(1.2, 7.0 - min(I, 12) * 0.4)

    eq_v = 34 + 26 * v_norm
    eq_i = 34 + 26 * i_norm
    eq_r = 34 + 26 * r_norm

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

      <rect x="10" y="10" width="960" height="680" rx="24" fill="#ffffff" stroke="#e5e7eb" stroke-width="2"></rect>

      <text x="35" y="45" font-size="28" font-weight="700" fill="#111827">
        Visualisasi Rangkaian Hukum Ohm
      </text>
      <text x="35" y="72" font-size="16" fill="#6b7280">
        Baterai, resistor, persamaan, dan arus berubah sesuai nilai slider.
      </text>

      <path id="currentPath" d="M 250 105 L 760 105" fill="none" stroke="none"></path>

      <line x1="250" y1="105" x2="{arrow_end}" y2="105"
            stroke="#2563eb" stroke-width="{arrow_thickness}" marker-end="url(#arrowHead)"></line>

      <circle cx="0" cy="0" r="5" fill="#2563eb">
        <animateMotion dur="{anim_dur}s" repeatCount="indefinite">
          <mpath href="#currentPath"></mpath>
        </animateMotion>
      </circle>
      <circle cx="0" cy="0" r="5" fill="#60a5fa">
        <animateMotion dur="{anim_dur}s" begin="-1.7s" repeatCount="indefinite">
          <mpath href="#currentPath"></mpath>
        </animateMotion>
      </circle>
      <circle cx="0" cy="0" r="5" fill="#93c5fd">
        <animateMotion dur="{anim_dur}s" begin="-3.1s" repeatCount="indefinite">
          <mpath href="#currentPath"></mpath>
        </animateMotion>
      </circle>

      <text x="505" y="85" text-anchor="middle" font-size="{current_font}" font-weight="800" fill="#ea580c">
        I = {I:.2f} A
      </text>

      <line x1="200" y1="140" x2="470" y2="140" stroke="#111827" stroke-width="5"></line>
      <polyline points="{zigzag}" fill="none" stroke="{res_color}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"></polyline>
      <line x1="{resistor_x + resistor_len}" y1="140" x2="800" y2="140" stroke="#111827" stroke-width="5"></line>
      <line x1="800" y1="140" x2="800" y2="380" stroke="#111827" stroke-width="5"></line>
      <line x1="800" y1="380" x2="200" y2="380" stroke="#111827" stroke-width="5"></line>
      <line x1="200" y1="140" x2="200" y2="{battery_top}" stroke="#111827" stroke-width="5"></line>
      <line x1="200" y1="{battery_bottom}" x2="200" y2="380" stroke="#111827" stroke-width="5"></line>

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

      <text x="{resistor_x + resistor_len/2}" y="{resistor_y + resistor_amp + 48}" text-anchor="middle"
            font-size="{resistor_font}" font-weight="800" fill="{res_color}">
        R = {R:.2f} Ω
      </text>

      <rect x="60" y="450" width="400" height="180" rx="18" fill="#f8fafc" stroke="#cbd5e1"></rect>
      <text x="85" y="485" font-size="24" font-weight="700" fill="#111827">Persamaan Dinamis</text>
      <text x="105" y="550" font-size="{eq_v}" font-weight="900" fill="#2563eb">V</text>
      <text x="165" y="550" font-size="40" font-weight="800" fill="#111827">=</text>
      <text x="220" y="550" font-size="{eq_i}" font-weight="900" fill="#ea580c">I</text>
      <text x="275" y="550" font-size="{eq_r}" font-weight="900" fill="{res_color}">R</text>
      <text x="85" y="600" font-size="22" fill="#374151">{V:.2f} = {I:.2f} × {R:.2f}</text>

      <rect x="500" y="450" width="400" height="180" rx="18" fill="#fff7ed" stroke="#fed7aa"></rect>
      <text x="525" y="485" font-size="24" font-weight="700" fill="#9a3412">Makna Fisika</text>
      <text x="525" y="525" font-size="20" fill="#7c2d12">• V naik → I naik, jika R tetap</text>
      <text x="525" y="555" font-size="20" fill="#7c2d12">• R naik → I turun, jika V tetap</text>
      <text x="525" y="585" font-size="20" fill="#7c2d12">• Panah menunjukkan arah arus</text>
      <text x="525" y="615" font-size="20" fill="#7c2d12">• Warna resistor menunjukkan besar hambatan</text>
    </svg>
    """
    return svg

# =========================
# HEADER
# =========================
st.markdown('<div class="title-main">Simulasi Hukum Ohm Interaktif</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle-main">Versi ini menambahkan latihan prediksi, pengecekan jawaban, dan pencatatan hasil percobaan.</div>',
    unsafe_allow_html=True
)

# =========================
# INPUT UTAMA
# =========================
col_a, col_b = st.columns([1, 1])

with col_a:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.subheader("Kontrol Utama")
    V = st.slider("Tegangan (V)", 0.0, 24.0, 12.0, 0.5)
    R = st.slider("Hambatan (Ω)", 1.0, 20.0, 6.0, 0.5)
    I = V / R
    st.markdown('<div class="note-text">Geser slider lalu amati perubahan visualisasi dan hasil perhitungan.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_b:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.subheader("Makna Cepat")
    st.write(f"Nilai arus saat ini adalah {I:.2f} A.")
    st.write("Arus bertambah jika tegangan bertambah.")
    st.write("Arus berkurang jika hambatan bertambah.")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# METRIK
# =========================
m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Tegangan</div>
        <div class="metric-blue">{V:.2f} V</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Hambatan</div>
        <div class="metric-green">{R:.2f} Ω</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Arus</div>
        <div class="metric-orange">{I:.2f} A</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# =========================
# VISUALISASI
# =========================
left, right = st.columns([2, 1])

with left:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.subheader("Visualisasi Dinamis")
    components.html(build_svg(V, R, I), height=720, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.subheader("Ringkasan Perhitungan")
    st.write(f"Persamaan: {V:.2f} = {I:.2f} × {R:.2f}")
    st.write(f"Arus hasil perhitungan: {I:.2f} A")
    if R < 7:
        st.success("Hambatan rendah")
    elif R < 14:
        st.warning("Hambatan sedang")
    else:
        st.error("Hambatan tinggi")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# LATIHAN SISWA
# =========================
st.markdown('<div class="panel-box">', unsafe_allow_html=True)
st.subheader("Latihan Prediksi Arus")

pred_col1, pred_col2, pred_col3 = st.columns([1, 1, 1])

with pred_col1:
    prediksi_arus = st.number_input("Prediksi arus Anda (A)", min_value=0.0, step=0.1, format="%.2f")

with pred_col2:
    toleransi = st.number_input("Toleransi jawaban", min_value=0.01, value=0.20, step=0.01, format="%.2f")

with pred_col3:
    alasan = st.text_area("Alasan prediksi", placeholder="Tuliskan alasan singkat Anda", height=100)

cek1, cek2, cek3 = st.columns([1, 1, 1])

with cek1:
    if st.button("Cek Jawaban", use_container_width=True):
        st.session_state.show_answer = True

with cek2:
    if st.button("Sembunyikan Jawaban", use_container_width=True):
        st.session_state.show_answer = False

with cek3:
    if st.button("Tambah ke Tabel Percobaan", use_container_width=True):
        st.session_state.records.append({
            "Tegangan (V)": round(V, 2),
            "Hambatan (Ω)": round(R, 2),
            "Prediksi Arus (A)": round(prediksi_arus, 2),
            "Arus Sebenarnya (A)": round(I, 2),
            "Selisih": round(abs(prediksi_arus - I), 2),
            "Alasan": alasan
        })

if st.session_state.show_answer:
    selisih = abs(prediksi_arus - I)
    st.write(f"Arus sebenarnya adalah {I:.2f} A.")
    if selisih <= toleransi:
        st.success(f"Prediksi Anda tepat. Selisih {selisih:.2f} A.")
    else:
        st.error(f"Prediksi Anda belum tepat. Selisih {selisih:.2f} A.")
st.markdown('</div>', unsafe_allow_html=True)

# =========================
# TABEL HASIL PERCOBAAN
# =========================
st.markdown('<div class="panel-box">', unsafe_allow_html=True)
st.subheader("Tabel Percobaan Siswa")

if st.session_state.records:
    df_records = pd.DataFrame(st.session_state.records)
    st.dataframe(df_records, use_container_width=True)

    b1, b2 = st.columns([1, 1])

    with b1:
        csv = df_records.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Unduh Data CSV",
            data=csv,
            file_name="hasil_percobaan_hukum_ohm.csv",
            mime="text/csv",
            use_container_width=True
        )

    with b2:
        if st.button("Reset Tabel Percobaan", use_container_width=True):
            st.session_state.records = []
            st.rerun()
else:
    st.info("Belum ada data percobaan yang ditambahkan.")
st.markdown('</div>', unsafe_allow_html=True)

# =========================
# DATA OTOMATIS DAN GRAFIK
# =========================
t1, t2 = st.columns([1, 1])

voltages = np.arange(0, 25, 2)
currents = voltages / R
df_auto = pd.DataFrame({
    "Tegangan (V)": voltages,
    "Hambatan (Ω)": [R] * len(voltages),
    "Arus (A)": np.round(currents, 3)
})

with t1:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.subheader("Tabel Data Otomatis")
    st.dataframe(df_auto, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with t2:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.subheader("Grafik I terhadap V")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(voltages, currents, marker="o")
    ax.set_xlabel("Tegangan (V)")
    ax.set_ylabel("Arus (A)")
    ax.set_title(f"Hubungan I terhadap V pada R = {R:.2f} Ω")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# REFLEKSI
# =========================
st.markdown('<div class="panel-box">', unsafe_allow_html=True)
st.subheader("Refleksi")
st.write("Apa yang terjadi pada arus ketika tegangan dinaikkan tetapi hambatan tetap?")
st.write("Apa yang terjadi pada arus ketika hambatan dinaikkan tetapi tegangan tetap?")
st.write("Apakah hasil prediksi Anda sudah sesuai dengan rumus Hukum Ohm?")
st.markdown('</div>', unsafe_allow_html=True)
