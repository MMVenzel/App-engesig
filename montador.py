import streamlit as st
from PIL import Image
import base64
from pathlib import Path
import matplotlib.pyplot as plt
import io
from fpdf import FPDF
import datetime

# --- CONFIG INICIAL ---
st.set_page_config(
    page_title="Engesig | Central de Custos",
    page_icon="logo_engesig.ico"
)

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    :root {
        color-scheme: dark;
    }
    .stApp {
        background-color: black !important;
        color: white !important;
    }
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', sans-serif;
        font-size: 16px;
        color: white;
    }
    h1, h2, h3, h4, h5, h6, p, label, div, span {
        color: white !important;
    }
    .stSelectbox div[data-baseweb="select"] *,
    .stSelectbox input, input[type="number"] {
        color: white !important;
        background-color: rgba(30, 30, 30, 0.7) !important;
    }
    div[data-baseweb="popover"] * {
        color: white !important;
        background-color: #333 !important;
    }
    header, [data-testid="stHeader"] {
        visibility: hidden;
        height: 0rem;
        padding: 0rem;
    }
    input:focus, select:focus, textarea:focus, .stSelectbox:focus-within {
        animation: pulse 0.6s;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 0, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }
    }
    .botao-pdf-flutuante {
        position: relative;
        top: 290px;
        right: 300px;
        z-index: 10001;
    }
    .download-pdf-flutuante {
        position: fixed;
        top: 340px;
        right: 300x;
        z-index: 10001;
    }
    /* Corrige visual de botões em qualquer tema */
    button {
        background-color: #222 !important;
        color: white !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
        padding: 0.5em 1em !important;
        transition: 0.3s ease;
    }
    button:hover {
        background-color: #333 !important;
        border: 1px solid white !important;
        color: white !important;
    }
    /* Corrige ícones dentro dos botões */
    button svg {
        fill: white !important;
    }
    /* Apenas define a largura, a altura será ajustada automaticamente */
    .grafico-fixo {
        width: 300px;
        z-index: 10000;
        background: none;
        position: fixed;
        top: 290px;
        left: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# --- DADOS ---
precos_amplificador = {"Nenhum": 0, "100W": 338.19, "200W": 547.47, "Moto": 392.55}
preco_driver = 319.81
precos_controlador = {
    "Nenhum": 0, "Micro 3B Moto": 102.98, "Micro 3B C/ Mic": 145.50, "Micro 4B com Mic": 145.36,
    "Handheld 9B Magnético": 236.44, "Controlador Fixo 15B": 206.30, "Controlador Fixo 17B": 216.60
}
precos_modulo = {"Nenhum": 0, "Nano": 39.67, "Micro": 25.69, "D-Max": 28.17, "Sinalizador": 25.69}
precos_sinalizador_teto = {"Nenhum": 0, "Sirius": 100.00, "Brutale": 100.00}
precos_kit_sinalizador = {"Sirius": 3, "Brutale": 7}
precos_tipo_led_config = {
    "Nano": {"3W": {"Single": 20.90, "Dual": 31.27, "Tri": 33.51}},
    "Micro": {
        "3W": {"Single": 14.89, "Dual": 19.09, "Tri": 20.56},
        "OPT": {"Single": 13.97},
        "Q-MAX": {"Single": 7.3},
    },
    "D-Max": {
        "3W": {"Single": 15.2, "Dual": 18.94, "Tri": 23.51},
        "OPT": {"Single": 15.31},
        "Q-MAX": {"Single": 9.1},
    },
    "Sinalizador": {
        "3W": {"Single": 14.89, "Dual": 19.09, "Tri": 20.56},
        "OPT": {"Single": 13.97},
        "Q-MAX": {"Single": 7.3},
    }
}
precos_cor_led = {
    "3W": {"Amber": 5.79, "Red": 3.58, "Blue": 3.58, "White": 3.58},
    "OPT": {"Amber": 1.36, "Red": 0.86, "Blue": 1.00, "White": 1.60},
    "Q-MAX": {"Amber": 1.36, "Red": 0.86, "Blue": 1.00, "White": 1.60}
}
limite_cores = {
    ("Nano", "3W"): 3,
    ("Micro", "3W"): 3,
    ("Micro", "OPT"): 1,
    ("Micro", "Q-MAX"): 1,
    ("D-Max", "3W"): 3,
    ("D-Max", "OPT"): 2,
    ("D-Max", "Q-MAX"): 1,
    ("Sinalizador", "3W"): 3,
    ("Sinalizador", "OPT"): 1,
    ("Sinalizador", "Q-MAX"): 1
}
# --- FUNÇÃO PDF ---
def gerar_pdf(amplificador, valor_amplificador, qtd_driver, valor_driver,
              controlador_tipo, valor_controlador, valores_modulos,
              valor_total_modulos, sinalizador_tipo, valor_total_sinalizador,
              total, img_bytes):

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Título
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Relatório de Custo - Sinalização", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(5)

    # Data
    data = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.cell(200, 10, txt=f"Data: {data}", ln=True)

    # Detalhes dos componentes
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Amplificador: {amplificador} - R$ {valor_amplificador:.2f}", ln=True)
    if qtd_driver:
        pdf.cell(200, 10, txt=f"Driver(s): {qtd_driver} - R$ {valor_driver:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Controlador: {controlador_tipo} - R$ {valor_controlador:.2f}", ln=True)

    # Módulos Auxiliares
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Módulos Auxiliares:", ln=True)
    pdf.set_font("Arial", size=12)
    for idx, valor in enumerate(valores_modulos):
        pdf.cell(200, 10, txt=f"Configuração Módulo #{idx+1}: R$ {valor:.2f}", ln=True)

    pdf.cell(200, 10, txt=f"Total Módulos: R$ {valor_total_modulos:.2f}", ln=True)

    # Sinalizador de Teto
    if valor_total_sinalizador > 0:
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Sinalizador de Teto:", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Tipo: {sinalizador_tipo} - R$ {valor_total_sinalizador:.2f}", ln=True)

    # Total Geral
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"TOTAL: R$ {total:.2f}", ln=True)

    # Adiciona o gráfico se existir
    if img_bytes and img_bytes.getbuffer().nbytes > 0:
        img_path = "grafico_temp.png"
        with open(img_path, "wb") as f:
            f.write(img_bytes.getbuffer())
        pdf.image(img_path, x=50, y=None, w=100)

    return pdf.output(dest='S').encode('latin-1')

# --- ENTRADAS ---
st.title("Central de Custos | Sinalização")
amplificador = st.selectbox("Escolha o amplificador:", list(precos_amplificador.keys()))
qtd_driver = 0
if amplificador in ["100W", "200W"]:
    if st.selectbox("Acompanha driver?", ["Não", "Sim"]) == "Sim":
        qtd_driver = 1 if amplificador == "100W" else 2
controlador_tipo = st.selectbox("Escolha o tipo de controlador:", list(precos_controlador.keys()))

# --- MÓDULOS AUXILIARES ---
st.markdown("### 🔧 Módulos Auxiliares")
qtd_modelos_modulos = st.number
