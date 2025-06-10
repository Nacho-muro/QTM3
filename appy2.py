import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def simular_valores_futuros(precio, eps, año_inicio, año_fin, ajuste):
    años = range(año_inicio, año_fin + 1)
    datos = []
    for año in años:
        precio_simulado = precio * (ajuste ** (año - 2025)) if precio else np.nan
        eps_simulado = eps * (ajuste ** (año - 2025)) if eps else np.nan
        datos.append({
            "Año": año,
            "Precio futuro simulado": precio_simulado,
            "EPS futuro simulado": eps_simulado
        })
    return pd.DataFrame(datos)

st.title("Simulación de valoración futura (como si usara IBM Quantum)")

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

        # --- Explicación de los factores externos ---
        st.subheader("Factores externos aplicados")
        st.write("Los factores externos se aplican automáticamente para ajustar el valor futuro de la empresa. Estos factores incluyen:")
        st.write("- **Inflación:** Mide el aumento general de los precios en la economía. Una inflación alta puede reducir el poder adquisitivo y afectar los costos de la empresa.")
        st.write("- **Tasa de interés:** Impacta en el coste del endeudamiento y en las decisiones de inversión. Una tasa alta puede frenar el crecimiento económico.")
        st.write("- **Sentimiento tecnológico:** Refleja la confianza y el optimismo en el sector tecnológico. Un valor positivo indica un entorno favorable para la innovación.")
        st.write("- **Estabilidad política:** Mide el grado de estabilidad y previsibilidad del entorno político. Una alta estabilidad favorece la inversión y el crecimiento.")
        st.write("")
        st.write("En el futuro, estos factores podrían ser filtrados y ponderados por una IA para enviar los datos más relevantes a IBM Quantum y obtener proyecciones más precisas.")
        st.write("")

        st.subheader("Escenarios de simulación")
        st.write("Se muestran tres líneas de valoración para los próximos 20 años (2026-2045):")
        st.write("- **Optimista:** Factores externos muy favorables (crecimiento alto).")
        st.write("- **Base:** Factores externos normales (crecimiento moderado).")
        st.write("- **Conservadora:** Factores externos adversos (crecimiento bajo o negativo).")
        st.write("")
        st.write("La simulación funciona incluso si no hay PER o EPS disponible, como si IBM Quantum pudiera trabajar con cualquier dato recibido.")

        # --- Barra para seleccionar años (afecta solo a la tabla) ---
        st.subheader("Selecciona los años para la tabla")
        año_inicio = 2026
        año_fin = 2045
        años_seleccionados = st.slider(
            "Elige el rango de años para la tabla",
            min_value=año_inicio,
            max_value=año_fin,
            value=(año_inicio, año_fin)
        )
        años_tabla = list(range(años_seleccionados[0], años_seleccionados[1] + 1))

        # --- Ajustes para cada escenario ---
        ajuste_optimista = 1.05
        ajuste_base = 1.02
        ajuste_conservador = 0.99

        # --- Simulación para cada escenario ---
        df_optimista = simular_valores_futuros(precio, eps, año_inicio, año_fin, ajuste_optimista)
        df_base = simular_valores_futuros(precio, eps, año_inicio, año_fin, ajuste_base)
        df_conservador = simular_valores_futuros(precio, eps, año_inicio, año_fin, ajuste_conservador)

        # --- Tabla con los valores base para los años seleccionados ---
        df_tabla = df_base[df_base["Año"].isin(años_tabla)]
        st.subheader(f"Valores simulados para los años {años_seleccionados[0]}-{años_seleccionados[1]} (escenario base)")
        st.dataframe(df_tabla.style.format({
            "Precio futuro simulado": "{:.2f}",
            "EPS futuro simulado": "{:.2f}"
        }))

        # --- Gráfica con las tres líneas de valoración (siempre 20 años) ---
        st.subheader("Evolución de los valores simulados (2026-2045)")
        fig, ax = plt.subplots(figsize=(10, 6))
        if precio:
            ax.plot(df_optimista["Año"], df_optimista["Precio futuro simulado"], 'r-', label="Optimista (Precio)")
            ax.plot(df_base["Año"], df_base["Precio futuro simulado"], 'b-', label="Base (Precio)")
            ax.plot(df_conservador["Año"], df_conservador["Precio futuro simulado"], 'g-', label="Conservadora (Precio)")
        if eps:
            ax.plot(df_optimista["Año"], df_optimista["EPS futuro simulado"], 'r:', label="Optimista (EPS)")
            ax.plot(df_base["Año"], df_base["EPS futuro simulado"], 'b:', label="Base (EPS)")
            ax.plot(df_conservador["Año"], df_conservador["EPS futuro simulado"], 'g:', label="Conservadora (EPS)")
        ax.set_xlabel("Año")
        ax.set_ylabel("Valor")
        ax.set_title(f"Evolución de los valores simulados para {nombre} ({ticker})")
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"No se pudo obtener información o ejecutar la simulación: {e}")
