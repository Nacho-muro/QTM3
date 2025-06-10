import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def simular_valores_futuros(per, eps, precio, año_inicio, año_fin, ajuste):
    años = range(año_inicio, año_fin + 1)
    datos = []
    for año in años:
        per_simulado = per * (ajuste ** (año - 2025))
        eps_simulado = eps * (ajuste ** (año - 2025))
        precio_simulado = precio * (ajuste ** (año - 2025)) if precio else np.nan
        datos.append({
            "Año": año,
            "PER simulado": per_simulado,
            "EPS simulado": eps_simulado,
            "Precio futuro simulado": precio_simulado
        })
    return pd.DataFrame(datos)

st.title("Simulación de valoración futura con diferentes escenarios")

ticker = st.text_input("Introduce el ticker de la empresa (ej: AMZN, AAPL, GOOGL, TSLA)")
if ticker.strip():
    ticker = ticker.strip().upper()
    try:
        empresa = yf.Ticker(ticker)
        info = empresa.info
        nombre = info.get("shortName", ticker)
        per = info.get("trailingPE", None)
        eps = info.get("trailingEps", None)
        precio = info.get("currentPrice", None)
        moneda = info.get("currency", "USD")
        sector = info.get("sector", "Desconocido")

        st.subheader(f"{nombre} ({ticker}) - Sector: {sector}")
        st.write(f"**Precio actual:** {precio} {moneda}" if precio else "Precio actual: No disponible")
        st.write(f"**PER:** {per if per else 'No disponible'}")
        st.write(f"**EPS:** {eps if eps else 'No disponible'}")

        if per is None or eps is None:
            st.warning("No hay suficientes datos financieros para simular el valor futuro.")
        else:
            per = float(per)
            eps = float(eps)

            # Explicación de los escenarios
            st.subheader("Escenarios de simulación")
            st.write("Se muestran tres líneas de valoración para los próximos 20 años (2026-2045):")
            st.write("- **Optimista:** Factores externos muy favorables (crecimiento alto).")
            st.write("- **Base:** Factores externos normales (crecimiento moderado).")
            st.write("- **Conservadora:** Factores externos adversos (crecimiento bajo o negativo).")
            st.write("")
            st.write("En el futuro, estas proyecciones podrían ser generadas por IBM Quantum según los datos filtrados por una IA.")

            # Ajustes para cada escenario
            ajuste_optimista = 1.05  # Crecimiento alto
            ajuste_base = 1.02       # Crecimiento moderado (equivalente a los factores externos de ejemplo)
            ajuste_conservador = 0.99 # Crecimiento bajo o negativo

            # Simulación para cada escenario
            año_inicio = 2026
            año_fin = 2045
            df_optimista = simular_valores_futuros(per, eps, precio, año_inicio, año_fin, ajuste_optimista)
            df_base = simular_valores_futuros(per, eps, precio, año_inicio, año_fin, ajuste_base)
            df_conservador = simular_valores_futuros(per, eps, precio, año_inicio, año_fin, ajuste_conservador)

            # Tabla con los valores base (o puedes mostrar las tres tablas si prefieres)
            st.subheader("Valores simulados para el periodo 2026-2045 (escenario base)")
            st.dataframe(df_base.style.format({
                "PER simulado": "{:.2f}",
                "EPS simulado": "{:.2f}",
                "Precio futuro simulado": "{:.2f}"
            }))

            # Gráfica con las tres líneas de valoración
            st.subheader("Evolución de los valores simulados (2026-2045)")
            fig, ax = plt.subplots(figsize=(10, 6))
            if precio:
                ax.plot(df_optimista["Año"], df_optimista["Precio futuro simulado"], 'r-', label="Optimista (Precio)")
                ax.plot(df_base["Año"], df_base["Precio futuro simulado"], 'b-', label="Base (Precio)")
                ax.plot(df_conservador["Año"], df_conservador["Precio futuro simulado"], 'g-', label="Conservadora (Precio)")
            ax.plot(df_optimista["Año"], df_optimista["PER simulado"], 'r--', label="Optimista (PER)")
            ax.plot(df_base["Año"], df_base["PER simulado"], 'b--', label="Base (PER)")
            ax.plot(df_conservador["Año"], df_conservador["PER simulado"], 'g--', label="Conservadora (PER)")
            ax.plot(df_optimista["Año"], df_optimista["EPS simulado"], 'r:', label="Optimista (EPS)")
            ax.plot(df_base["Año"], df_base["EPS simulado"], 'b:', label="Base (EPS)")
            ax.plot(df_conservador["Año"], df_conservador["EPS simulado"], 'g:', label="Conservadora (EPS)")
            ax.set_xlabel("Año")
            ax.set_ylabel("Valor")
            ax.set_title(f"Evolución de los valores simulados para {nombre} ({ticker})")
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True)
            st.pyplot(fig)
    except Exception as e:
        st.error(f"No se pudo obtener información o ejecutar la simulación: {e}")
