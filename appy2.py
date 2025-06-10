import streamlit as st
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

EXPLICACIONES = {
    "Quantum Monte Carlo": "Este algoritmo permite simular escenarios de mercado y estimar el valor futuro de la empresa bajo diferentes condiciones económicas.",
    "QAOA": "QAOA optimiza la combinación de empresas en una cartera para maximizar el rendimiento y minimizar el riesgo.",
    "Grover's Algorithm": "Grover puede buscar, entre miles de empresas, aquellas con mejor potencial de crecimiento según ciertos criterios.",
    "HHL Algorithm": "HHL resuelve sistemas complejos de ecuaciones para predecir el comportamiento financiero de la empresa."
}

# Diccionario de empresas de referencia por sector
REFERENCIAS_SECTOR = {
    "Technology": ["AAPL", "MSFT", "GOOGL", "AMZN", "META"],
    "Consumer Cyclical": ["TSLA", "NFLX", "SBUX"],
    "Healthcare": ["AMGN", "GILD", "BIIB"],
}

def valor_esperado_cuantico(per, eps, inflacion=0, tasa_interes=0, sentimiento=0):
    # Normalizar factores externos
    inflacion_norm = min(max(inflacion, -10), 10) / 10
    tasa_norm = min(max(tasa_interes, 0), 10) / 10
    sentimiento_norm = min(max(sentimiento, -1), 1)
    # Ponderar el impacto de los factores externos
    impacto_externo = 0.2 * inflacion_norm + 0.3 * tasa_norm + 0.5 * sentimiento_norm
    # Simulación del valor esperado cuántico
    per_norm = min(max(per, 0), 100) / 100 * np.pi
    eps_norm = min(max(eps, 0), 10) / 10 * np.pi
    theta = per_norm + eps_norm + impacto_externo * np.pi
    return np.sin(theta)

st.title("Valoración Cuántica de Empresas (Simulación)")

ticker = st.text_input("Introduce el ticker de la empresa (ej: AMZN, AAPL, GOOGL, TSLA)")
algoritmo = st.selectbox("Selecciona el algoritmo cuántico", list(EXPLICACIONES.keys()))
calcular = st.button("Optimizar con simulación cuántica")

st.caption("Esta demo obtiene datos reales y simula el análisis cuántico localmente, incluyendo factores externos. Preparada para un futuro salto a hardware cuántico real.")

if calcular and ticker.strip():
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
            st.warning("No hay suficientes datos financieros para optimizar cuánticamente esta empresa.")
        else:
            try:
                per = float(per)
                eps = float(eps)
            except (TypeError, ValueError):
                st.error("Error al convertir PER o EPS a número. Verifica los datos.")
                st.stop()

            # Factores externos simulados
            st.subheader("Factores externos (simulados)")
            inflacion = st.slider("Inflación (%)", -10.0, 10.0, 2.0)
            tasa_interes = st.slider("Tasa de interés (%)", 0.0, 10.0, 2.0)
            sentimiento = st.slider("Sentimiento de mercado (-1 a 1)", -1.0, 1.0, 0.0)

            # Simulación del valor esperado cuántico con factores externos
            valor_cuantico = valor_esperado_cuantico(per, eps, inflacion, tasa_interes, sentimiento)
            st.success(f"Resultado cuántico (simulado con factores externos): {valor_cuantico:.3f}")
            if valor_cuantico > 0:
                st.write("**Interpretación:** El análisis cuántico sugiere una perspectiva positiva para la empresa.")
            else:
                st.write("**Interpretación:** El análisis cuántico sugiere cautela o perspectiva negativa para la empresa.")

            # Gráfico de precio histórico
            st.subheader("Precio histórico")
            hist = empresa.history(period="1y")
            if not hist.empty:
                fig, ax = plt.subplots()
                ax.plot(hist.index, hist['Close'])
                ax.set_title(f"Precio histórico de {nombre} ({ticker})")
                ax.set_ylabel("Precio (USD)")
                st.pyplot(fig)
            else:
                st.warning("No hay datos históricos disponibles.")

            # Comparativa con el sector (valores reales)
            st.subheader("Comparativa con el sector (valores reales)")
            tickers_comparar = REFERENCIAS_SECTOR.get(sector, [])
            datos_comparativa = []
            for ticker_c in tickers_comparar:
                if ticker_c == ticker:
                    continue
                empresa_c = yf.Ticker(ticker_c)
                info_c = empresa_c.info
                nombre_c = info_c.get("shortName", ticker_c)
                per_c = info_c.get("trailingPE", None)
                eps_c = info_c.get("trailingEps", None)
                if per_c is not None and eps_c is not None:
                    valor_cuantico_c = valor_esperado_cuantico(per_c, eps_c, inflacion, tasa_interes, sentimiento)
                    datos_comparativa.append((nombre_c, ticker_c, per_c, eps_c, valor_cuantico_c))
            if datos_comparativa:
                st.write(f"Empresas del sector {sector}:")
                for nombre_c, ticker_c, per_c, eps_c, valor_cuantico_c in datos_comparativa:
                    st.write(f"{nombre_c} ({ticker_c}): PER={per_c:.1f}, EPS={eps_c:.1f}, Valor cuántico simulado={valor_cuantico_c:.3f}")
            else:
                st.warning(f"No se encontraron empresas del mismo sector ({sector}) para comparar.")

            # Evolución del valor esperado cuántico simulado según los años seleccionados
            st.subheader("Evolución del valor esperado cuántico (simulado)")
            hist = empresa.history(period="max")
            if hist.empty:
                st.warning("No hay datos históricos disponibles para simular.")
            else:
                años_disponibles = hist.index.year.unique()
                año_min = int(min(años_disponibles))
                año_max = int(max(años_disponibles))
                año_inicio, año_fin = st.slider(
                    "Selecciona el rango de años",
                    min_value=año_min,
                    max_value=año_max,
                    value=(max(año_min, año_max - 5), año_max)
                )
                hist_filtrado = hist[(hist.index.year >= año_inicio) & (hist.index.year <= año_fin)]
                if hist_filtrado.empty:
                    st.warning("No hay datos históricos en el rango seleccionado.")
                else:
                    # Simular PER y EPS proporcionalmente al precio (aproximación)
                    precio_actual = info.get("currentPrice", 1)
                    per_actual = float(per) if per else 30.0
                    eps_actual = float(eps) if eps else 6.0
                    per_simulado = hist_filtrado["Close"] / (hist_filtrado["Close"].mean() / per_actual)
                    eps_simulado = hist_filtrado["Close"] / (hist_filtrado["Close"].mean() / eps_actual)
                    valores_esperados = []
                    fechas = []
                    for fecha, close, per_s, eps_s in zip(hist_filtrado.index, hist_filtrado["Close"], per_simulado, eps_simulado):
                        valores_esperados.append(valor_esperado_cuantico(per_s, eps_s, inflacion, tasa_interes, sentimiento))
                        fechas.append(fecha)
                    fig, ax = plt.subplots()
                    ax.plot(fechas, valores_esperados, marker='o')
                    ax.set_title(f"Evolución del valor esperado cuántico simulado ({año_inicio}-{año_fin})")
                    ax.set_ylabel("Valor esperado cuántico (simulado)")
                    ax.set_xlabel("Fecha")
                    st.pyplot(fig)

        st.markdown("---")
        st.write(EXPLICACIONES[algoritmo])

    except Exception as e:
        st.error(f"No se pudo obtener información o ejecutar la simulación cuántica: {e}")
elif calcular:
    st.warning("Por favor, introduce el ticker de la empresa.")

st.caption("Este análisis es experimental y educativo. Los resultados cuánticos son simulados localmente, preparados para un futuro salto a hardware cuántico real.")
