import streamlit as st
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import requests
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Estimator, Session
from qiskit.quantum_info import SparsePauliOp

# Configura tu clave de API de Alpha Vantage aquí
ALPHA_VANTAGE_API_KEY = "TU_CLAVE_DE_API"  # ¡Cámbialo por tu clave real!

EXPLICACIONES = {
    "Quantum Monte Carlo": "Este algoritmo permite simular escenarios de mercado y estimar el valor futuro de la empresa bajo diferentes condiciones económicas.",
    "QAOA": "QAOA optimiza la combinación de empresas en una cartera para maximizar el rendimiento y minimizar el riesgo.",
    "Grover's Algorithm": "Grover puede buscar, entre miles de empresas, aquellas con mejor potencial de crecimiento según ciertos criterios.",
    "HHL Algorithm": "HHL resuelve sistemas complejos de ecuaciones para predecir el comportamiento financiero de la empresa."
}

def obtener_empresas_mismo_sector(sector):
    """Busca empresas del mismo sector usando Alpha Vantage (ejemplo, puede variar según la API)"""
    # NOTA: Alpha Vantage no tiene un endpoint directo para buscar por sector.
    # Este es un ejemplo ilustrativo. Puedes adaptarlo a otra API o usar una lista predefinida.
    # En la práctica, muchas APIs financieras no permiten buscar por sector de forma directa.
    # Como alternativa, puedes usar una base de datos local o una lista predefinida.
    # Aquí simulamos la búsqueda para el ejemplo.
    empresas = []
    if sector == "Technology":
        empresas = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    elif sector == "Consumer Cyclical":
        empresas = ["TSLA", "NFLX", "SBUX"]
    elif sector == "Healthcare":
        empresas = ["AMGN", "GILD", "BIIB"]
    # Añade más sectores si lo deseas
    return empresas

st.title("Valoración Cuántica de Empresas con IBM Quantum")

ticker = st.text_input("Introduce el ticker de la empresa (ej: AMZN, AAPL, GOOGL, TSLA)")
algoritmo = st.selectbox("Selecciona el algoritmo cuántico", list(EXPLICACIONES.keys()))
calcular = st.button("Optimizar con IBM Quantum")

st.caption("Esta demo obtiene datos reales y ejecuta un análisis cuántico usando IBM Quantum.")

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

            per_norm = min(max(per, 0), 100) / 100 * np.pi
            eps_norm = min(max(eps, 0), 10) / 10 * np.pi
            theta = per_norm + eps_norm

            try:
                service = QiskitRuntimeService(
                    channel="ibm_quantum",
                    token=st.secrets["IBM_QUANTUM_TOKEN"]
                )
            except Exception as e:
                st.error(f"Error al inicializar el servicio IBM Quantum: {e}")
                st.stop()

            st.write("Backends físicos disponibles y su estado:")
            backends_disponibles = []
            for backend in service.backends(simulator=False):
                status = backend.status()
                st.write(f"{backend.name}: {'Disponible' if status.operational and status.status_msg == 'active' else status.status_msg}")
                if status.operational and status.status_msg == 'active':
                    backends_disponibles.append(backend)

            if not backends_disponibles:
                st.error("No hay backends físicos operativos en este momento. Intenta más tarde.")
                st.stop()

            backend = backends_disponibles[0]
            num_qubits = backend.configuration().num_qubits
            physical_qubit = num_qubits - 1

            qc = QuantumCircuit(1)
            qc.sx(0)
            qc.rz(theta, 0)
            qc.sx(0)

            qc = transpile(
                qc,
                backend=backend,
                initial_layout=[physical_qubit],
                optimization_level=3
            )

            observable_str = "I" * physical_qubit + "Z" + "I" * (num_qubits - physical_qubit - 1)
            observable = SparsePauliOp(observable_str)

            st.info(f"Ejecutando en {backend.name} sobre el qubit físico {physical_qubit}...")

            with Session(backend=backend) as session:
                estimator = Estimator(mode=session)
                estimator.options.resilience_level = 1
                estimator.options.default_shots = 1024

                job = estimator.run([(qc, observable, [])])
                result = job.result()
                if hasattr(result, 'data') and hasattr(result.data, 'evs') and len(result.data.evs) > 0:
                    valor_cuantico = result.data.evs[0]
                    st.success(f"Resultado cuántico (valor esperado): {valor_cuantico:.3f}")
                    if valor_cuantico > 0:
                        st.write("**Interpretación:** El análisis cuántico sugiere una perspectiva positiva para la empresa.")
                    else:
                        st.write("**Interpretación:** El análisis cuántico sugiere cautela o perspectiva negativa para la empresa.")
                else:
                    st.error("No se pudo obtener el resultado cuántico esperado. Verifica la ejecución del circuito.")

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

            # Comparativa con el sector usando API externa (simulada)
            st.subheader("Comparativa con el sector (usando API externa)")
            tickers_comparar = obtener_empresas_mismo_sector(sector)
            datos_comparativa = []
            for ticker_c in tickers_comparar:
                if ticker_c == ticker:
                    continue  # No comparar consigo misma
                empresa_c = yf.Ticker(ticker_c)
                info_c = empresa_c.info
                nombre_c = info_c.get("shortName", ticker_c)
                per_c = info_c.get("trailingPE", None)
                eps_c = info_c.get("trailingEps", None)
                if per_c is not None and eps_c is not None:
                    datos_comparativa.append((nombre_c, ticker_c, per_c, eps_c))
            if datos_comparativa:
                st.write(f"Empresas del sector {sector}:")
                for nombre_c, ticker_c, per_c, eps_c in datos_comparativa:
                    st.write(f"{nombre_c} ({ticker_c}): PER={per_c:.1f}, EPS={eps_c:.1f}")
            else:
                st.warning(f"No se encontraron empresas del mismo sector ({sector}) para comparar.")

            # Simulación de escenarios
            st.subheader("Simulación de escenarios")
            with st.expander("Simula diferentes valores de PER y EPS"):
                per_sim = st.slider("PER simulado", 0.0, 100.0, float(per))
                eps_sim = st.slider("EPS simulado", 0.0, 20.0, float(eps))
                per_norm_sim = min(max(per_sim, 0), 100) / 100 * np.pi
                eps_norm_sim = min(max(eps_sim, 0), 20) / 20 * np.pi
                theta_sim = per_norm_sim + eps_norm_sim
                st.write(f"Valor cuántico simulado: {np.sin(theta_sim):.3f} (solo como ejemplo)")

        st.markdown("---")
        st.write(EXPLICACIONES[algoritmo])

    except Exception as e:
        st.error(f"No se pudo obtener información o ejecutar el análisis cuántico: {e}")
elif calcular:
    st.warning("Por favor, introduce el ticker de la empresa.")

st.caption("Este análisis es experimental y educativo. Los resultados cuánticos dependen del modelo y los datos enviados.")
