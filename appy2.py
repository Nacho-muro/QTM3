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
        per_simulado = precio_simulado / eps_simulado if precio_simulado and eps_simulado else np.nan
        valor_intrinseco_simulado = precio_simulado * 0.9  # Ejemplo simplificado
        datos.append({
            "Año": año,
            "Precio futuro simulado": precio_simulado,
            "EPS futuro simulado": eps_simulado,
            "PER futuro simulado": per_simulado,
            "Valor intrínseco futuro simulado": valor_intrinseco_simulado
        })
    return pd.DataFrame(datos)

page = st.sidebar.radio("Navegar", ["Inicio", "Conceptos clave"])

if page == "Inicio":
    st.title("Simulación Cuántica de Valoración Empresarial")
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

            st.subheader("Selecciona el rango de años para la tabla")
            año_inicio = 2026
            año_fin = 2045
            años_seleccionados = st.slider(
                "Elige el rango de años",
                min_value=año_inicio,
                max_value=año_fin,
                value=(año_inicio, año_fin)
            )
            años_tabla = list(range(años_seleccionados[0], años_seleccionados[1] + 1))

            ajuste_base = 1.02
            df_base = simular_valores_futuros(precio, eps, año_inicio, año_fin, ajuste_base)
            df_tabla = df_base[df_base["Año"].isin(años_tabla)]

            st.subheader("Valores simulados para los años seleccionados (escenario base)")
            st.dataframe(df_tabla.style.format({
                "Precio futuro simulado": "{:.2f}",
                "EPS futuro simulado": "{:.2f}",
                "PER futuro simulado": "{:.2f}",
                "Valor intrínseco futuro simulado": "{:.2f}"
            }))

            st.subheader("Factores externos considerados")
            st.write("""
            - **Situación económica:** Inflación, tasas de interés, crecimiento del PIB.
            - **Políticas y cuestiones legales:** Cambios regulatorios, estabilidad política.
            - **Tecnología:** Avances tecnológicos y su impacto en el sector.
            - **Aspectos sociales:** Cambios demográficos, tendencias de consumo.
            - **Competencia y mercado:** Dinámica competitive, cambios en la demanda.
            """)
            st.write("Estos factores se integran en los cálculos para ofrecer una valoración más precisa y adaptada al entorno real.")
            st.write("[Ver explicación detallada de los conceptos](Conceptos clave)")

            st.subheader("Evolución de los valores simulados (2026-2045)")
            fig, ax = plt.subplots(figsize=(10, 6))
            if precio:
                ax.plot(df_base["Año"], df_base["Precio futuro simulado"], 'b-', label="Precio futuro simulado")
                ax.plot(df_base["Año"], df_base["Valor intrínseco futuro simulado"], 'g-', label="Valor intrínseco futuro simulado")
            if eps:
                ax.plot(df_base["Año"], df_base["EPS futuro simulado"], 'r:', label="EPS futuro simulado")
            ax.set_xlabel("Año")
            ax.set_ylabel("Valor")
            ax.set_title(f"Evolución de los valores simulados para {nombre} ({ticker})")
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True)
            st.pyplot(fig)

        except Exception as e:
            st.error(f"No se pudo obtener información o ejecutar la simulación: {e}")

elif page == "Conceptos clave":
    st.title("Conceptos clave del mercado de valores")
    
    st.markdown("""
    ## Introducción al mercado de valores

    El **mercado de valores** es el lugar donde se compran y venden acciones, bonos y otros instrumentos financieros emitidos por empresas y gobiernos.  
    Su función principal es facilitar la inversión y el financiamiento, permitiendo a las empresas obtener capital para crecer y a los inversores participar de los beneficios económicos de esas empresas.

    El mercado de valores se divide en dos grandes segmentos:
    - **Mercado primario:** donde las empresas emiten nuevos valores para obtener financiación.
    - **Mercado secundario:** donde los inversores negocian valores ya emitidos entre sí, aportando liquidez y permitiendo la formación de precios según la oferta y la demanda.
    """)

    st.markdown("---")

    st.markdown("""
    ## Indicadores financieros clave

    **Estos indicadores te ayudarán a comprender mejor los resultados de las simulaciones y a tomar decisiones informadas.**
    """)

    with st.expander("EPS (Beneficio por acción)"):
        st.markdown("""
        **¿Qué es?**  
        El **EPS** (*Earnings Per Share*) mide la rentabilidad de una empresa por cada acción ordinaria en circulación.

        **Cálculo:**  
        $$
        \\text{EPS} = \\frac{\\text{Beneficio neto} - \\text{Dividendos preferentes}}{\\text{Número de acciones ordinarias en circulación}}
        $$

        **¿Por qué es importante?**  
        Un EPS alto indica que la empresa es más rentable por acción.  
        Es fundamental para comparar empresas del mismo sector y evaluar su crecimiento a lo largo del tiempo.
        """)

    with st.expander("PER (Ratio Precio/Beneficio)"):
        st.markdown("""
        **¿Qué es?**  
        El **PER** (*Price-to-Earnings Ratio*) mide cuánto está dispuesto a pagar el mercado por cada unidad de beneficio de la empresa.

        **Cálculo:**  
        $$
        \\text{PER} = \\frac{\\text{Precio de la acción}}{\\text{EPS}}
        $$

        **¿Por qué es importante?**  
        Un PER bajo puede indicar que la acción está infravalorada o que la empresa tiene problemas.  
        Un PER alto sugiere que el mercado espera un crecimiento futuro o que la acción está sobrevalorada.
        """)

    with st.expander("P/A (Precio/Activos)"):
        st.markdown("""
        **¿Qué es?**  
        El ratio **P/A** (*Price-to-Assets*) compara el precio de la acción con el valor contable de los activos netos por acción.

        **Cálculo:**  
        $$
        \\text{P/A} = \\frac{\\text{Precio de la acción}}{\\text{Valor contable por acción}}
        $$

        **¿Por qué es importante?**  
        Es especialmente relevante para empresas con muchos activos tangibles (bancos, inmobiliarias, etc.).
        """)

    with st.expander("Valor intrínseco"):
        st.markdown("""
        **¿Qué es?**  
        El **valor intrínseco** es una estimación del valor real o fundamental de una empresa o acción, basado en sus activos, pasivos, beneficios y perspectivas futuras, más allá de las fluctuaciones temporales del mercado.

        **Cálculo (simplificado):**  
        $$
        \\text{Valor Intrínseco} = \\text{Activos} - \\text{Pasivos}
        $$

        **Por acción:**  
        $$
        \\text{Valor Intrínseco por acción} = \\frac{\\text{Valor Intrínseco}}{\\text{Número de acciones en circulación}}
        $$

        **Métodos avanzados:**  
        El método más usado es el **descuento de flujos de caja (DCF)**, que actualiza los flujos futuros de caja esperados al valor presente, teniendo en cuenta el riesgo y la tasa de descuento.

        **¿Por qué es importante?**  
        Permite identificar si una acción está sobrevalorada o infravalorada comparando el valor intrínseco con el precio de mercado.
        """)

    st.markdown("---")

    st.markdown("""
    ## Factores externos que afectan a las empresas

    **Estos factores no dependen directamente de la gestión de la empresa, pero pueden influir en su valoración y desempeño.**
    """)

    with st.expander("Factores externos"):
        st.markdown("""
        **¿Qué son?**  
        Son variables del entorno que afectan el valor de una empresa, pero que no dependen directamente de su gestión.

        **Ejemplos:**  
        - **Situación económica:** Inflación, tasas de interés, crecimiento del PIB.
        - **Políticas y cuestiones legales:** Cambios regulatorios, estabilidad política.
        - **Tecnología:** Avances tecnológicos y su impacto en el sector.
        - **Aspectos sociales:** Cambios demográficos, tendencias de consumo.
        - **Competencia y mercado:** Dinámica competitiva, cambios en la demanda.

        **¿Por qué son importantes?**  
        Estos factores se integran en los cálculos para ofrecer una valoración más realista y adaptada al entorno actual.
        """)

    st.markdown("---")
    st.write("[Volver a la simulación](Inicio)")
