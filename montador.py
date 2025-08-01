import streamlit as st
from PIL import Image
import base64
from pathlib import Path

# Função para aplicar imagem de fundo
def set_background(image_file):
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{base64.b64encode(open(image_file, "rb").read()).decode()}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: white;
    }}

    h1, h2, h3, h4, h5, h6, p, label, div, span {{
        color: white !important;
    }}

    .stSelectbox div[data-baseweb="select"] * {{
        color: white !important;
        background-color: rgba(0, 0, 0, 0.6) !important;
    }}

    div[data-baseweb="popover"] * {{
        color: white !important;
        background-color: #333 !important;
    }}

    .stSelectbox input {{
        color: white !important;
    }}

    input[type="number"] {{
        color: white !important;
        background-color: rgba(0, 0, 0, 0.6) !important;
    }}

    .css-1cpxqw2, .css-1d391kg {{
        color: white !important;
    }}

    header {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# Aplica imagem de fundo
set_background("plano_de_fundo.jpg")

# Título
st.title("Central de Custos | Sinalização")

# Tabelas de preços
precos_amplificador = {
    "Nenhum": 0,
    "100W": 338.19,
    "200W": 547.47,
    "Moto": 392.55
}

preco_driver = 319.81

precos_controlador = {
    "Nenhum": 0,
    "Micro 3B Moto": 90.98,
    "Micro 3B C/ Mic": 1,
    "Micro 4B S/ Mic": 1,
    "Micro 4B com Mic": 137.32,
    "Handheld 9B Magnético": 216.44,
    "Handheld 15B": 194.57,
    "Handheld 18B": 1,
    "Controlador Fixo 15B": 1,
    "Controlador Fixo 17B": 1,
}

precos_modulo = {
    "Nenhum": 0,
    "Nano": 39.67,
    "Micro": 25.69,
    "D-Max": 28.67
}

precos_tipo_led = {
    "Q-Max": 0,
    "OPT": 0,
    "3W": 0
}

precos_cor_led = {
    "Q-Max": {"Ambar": 5, "Rubi": 1, "Blue": 1.5, "White": 3},
    "OPT": {"Ambar": 5, "Rubi": 1, "Blue": 1.5, "White": 3},
    "3W": {"Ambar": 5, "Rubi": 1, "Blue": 1.5, "White": 3},
}

# Entradas do usuário
amplificador = st.selectbox("Escolha o amplificador:", list(precos_amplificador.keys()))

if amplificador == "100W":
    qtd_driver = st.selectbox("Quantidade de drivers:", [0, 1])
elif amplificador == "200W":
    qtd_driver = st.selectbox("Quantidade de drivers:", [0, 2])
else:
    qtd_driver = 0

controlador_tipo = st.selectbox("Escolha o tipo de controlador:", list(precos_controlador.keys()))

st.markdown("### Módulo Auxiliar")

# Regras de compatibilidade entre módulo e tipo de LED
tipo_modulo = st.selectbox("Tipo de módulo:", list(precos_modulo.keys()))

if tipo_modulo == "Nenhum":
    tipo_led = None
    cor_led = None
    qtd_leds = 0
elif tipo_modulo == "Nano":
    tipo_led = "3W"
    st.markdown("Tipo de LED: 3W (fixo para módulo Nano)")
    cor_led = st.selectbox("Cor do LED:", list(precos_cor_led[tipo_led].keys()))
    qtd_leds = st.number_input("Quantidade de LEDs:", min_value=0, step=1)
else:
    tipo_led = st.selectbox("Tipo de LED:", list(precos_tipo_led.keys()))
    cor_led = st.selectbox("Cor do LED:", list(precos_cor_led[tipo_led].keys()))
    qtd_leds = st.number_input("Quantidade de LEDs:", min_value=0, step=1)

# Cálculo do custo total
total = precos_amplificador[amplificador]
total += qtd_driver * preco_driver
total += precos_controlador[controlador_tipo]
if tipo_modulo != "Nenhum":
    total += precos_modulo[tipo_modulo] + precos_tipo_led[tipo_led] + (qtd_leds * precos_cor_led[tipo_led][cor_led])

# Resultado final
st.subheader(f" Custo Estimado: R$ {total:.2f}")

# Rodapé no canto inferior esquerdo (corrigido)
st.markdown("""
    <style>
    .rodape {
        position: fixed;
        bottom: 0;
        left: 10px;
        color: white;
        font-size: 12px;
        z-index: 9999;
    }
    </style>
    <div class="rodape">
        © 2025 by Engesig. Created by Matteo Marques & Matheus Venzel
    </div>
""", unsafe_allow_html=True)

# Logo flutuante
logo_path = Path("logo.png")  # ajuste conforme a extensão real do arquivo
if logo_path.exists():
    logo_base64 = base64.b64encode(logo_path.read_bytes()).decode()
    st.markdown(f"""
        <style>
        .logo-fixa {{
            position: fixed;
            top: 40px;
            left: 40px;
            width: 160px;
            z-index: 10000;
        }}
        </style>
        <img class="logo-fixa" src="data:image/png;base64,{logo_base64}">
    """, unsafe_allow_html=True)
