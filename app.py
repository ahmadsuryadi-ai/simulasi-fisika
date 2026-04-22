import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Simulasi Hukum Ohm", layout="wide")

st.title("Simulasi Hukum Ohm")
st.write("Atur tegangan (V) dan hambatan (R) untuk melihat perubahan arus (I).")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Parameter")
    V = st.slider("Tegangan (V)", 0.0, 24.0, 12.0, 0.5)
    R = st.slider("Hambatan (Ω)", 1.0, 20.0, 6.0, 0.5)

    I = V / R

    st.metric("Tegangan", f"{V:.2f} V")
    st.metric("Hambatan", f"{R:.2f} Ω")
    st.metric("Arus", f"{I:.2f} A")

    st.info("Rumus Hukum Ohm: I = V / R")

with col2:
    st.subheader("Sketsa Rangkaian")
    st.markdown(
        f"""
        Tegangan sumber: {V:.2f} V  
        Hambatan: {R:.2f} Ω  
        Arus: {I:.2f} A
        """
    )

    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Ohm%27s_Law_Pie_chart.svg/512px-Ohm%27s_Law_Pie_chart.svg.png",
        caption="Ilustrasi hubungan besaran pada Hukum Ohm"
    )

st.subheader("Tabel Nilai")
voltages = np.arange(0, 25, 3)
currents = voltages / R

df = pd.DataFrame({
    "Tegangan (V)": voltages,
    "Hambatan (Ω)": [R] * len(voltages),
    "Arus (A)": currents
})

st.dataframe(df, use_container_width=True)

st.subheader("Grafik Arus terhadap Tegangan")
fig, ax = plt.subplots()
ax.plot(voltages, currents, marker="o")
ax.set_xlabel("Tegangan (V)")
ax.set_ylabel("Arus (A)")
ax.set_title(f"Grafik I terhadap V pada Hambatan Tetap R = {R:.2f} Ω")
ax.grid(True)
st.pyplot(fig)

st.subheader("Interpretasi")
st.write(
    f"Pada tegangan {V:.2f} V dan hambatan {R:.2f} Ω, arus yang mengalir adalah {I:.2f} A. "
    "Jika tegangan dinaikkan saat hambatan tetap, arus meningkat. Jika hambatan dinaikkan saat tegangan tetap, arus menurun."
)
