import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd

# --- Factores externos (simulados automáticamente) ---
def obtener_factores_externos():
    # Ejemplo: valores fijos o simulados para inflación, tasa de interés, sentimiento tecnológico y estabilidad política
    return {
        "inflacion": 2.5,  # %
        "tasa_interes": 2.0,  # %
        "sentimiento_tecnologico": 0.7,  # -1 a 1
        "estabilidad_politica": 0.8  # 0 a 1
    }

# --- Simulación de PER, EPS y precio futuro según factores externos ---
def simular_valores_futuros(per, eps, precio, años_futuros, factores):
    # Calculamos el ajuste global por factores externos
    # (ejemplo simplificado, puedes ajustar la fórmula según tus necesidades)
    ajuste = 1 + (factores["inflacion"] - 2) / 100 \
             + (factores["tasa_interes"] - 2) / 100 \
             + factores["sentimiento_tecnologico"] / 20 \
             + (factores["estabilidad_politica"] - 0.5) / 10
    ajuste = max(ajuste, 0.8)  # Evitamos valores negativos o demasiado bajos

    # Simulamos los valores para cada año futuro
    datos = []
    for año in años_futuros:
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

# --- Interfaz de usuario ---
st.title("Simulación de valoración futura con factores externos")

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
            factores = obtener_factores_externos()

            # --- Explicación de los factores externos ---
            st.subheader("Factores externos aplicados")
            st.write("Los factores externos se aplican automáticamente para ajustar el valor futuro de la empresa. Estos factores incluyen:")
            st.write("- **Inflación:** Mide el aumento general de los precios en la economía. Una inflación alta puede reducir el poder adquisitivo y afectar los costos de la empresa.")
            st.write("- **Tasa de interés:** Impacta en el coste del endeudamiento y en las decisiones de inversión. Una tasa alta puede frenar el crecimiento económico.")
            st.write("- **Sentimiento tecnológico:** Refleja la confianza y el optimismo en el sector tecnológico. Un valor positivo indica un entorno favorable para la innovación.")
            st.write("- **Estabilidad política:** Mide el grado de estabilidad y previsibilidad del entorno político. Una alta estabilidad favorece la inversión y el crecimiento.")
            st.write("")
            st.write("**Valores aplicados en esta simulación:**")
            st.write(f"- **Inflación:** {factores['inflacion']}%")
            st.write(f"- **Tasa de interés:** {factores['tasa_interes']}%")
            st.write(f"- **Sentimiento tecnológico:** {factores['sentimiento_tecnologico']:.2f} (de -1 a 1)")
            st.write(f"- **Estabilidad política:** {factores['estabilidad_politica']:.2f} (de 0 a 1)")

            # --- Selección de años futuros ---
            st.subheader("Selecciona los años futuros a simular")
            años_futuros = st.multiselect(
                "Años futuros",
                options=[2026, 2027, 2028, 2029, 2030],
                default=[2026, 2027, 2028]
            )
            if años_futuros:
                df = simular_valores_futuros(per, eps, precio, años_futuros, factores)
                st.subheader("Valores simulados para los años seleccionados")
                st.dataframe(df.style.format({
                    "PER simulado": "{:.2f}",
                    "EPS simulado": "{:.2f}",
                    "Precio futuro simulado": "{:.2f}"
                }))
    except Exception as e:
        st.error(f"No se pudo obtener información o ejecutar la simulación: {e}")
