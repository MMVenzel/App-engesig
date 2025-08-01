import streamlit as st
from PIL import Image
import base64

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
    </style>
    """, unsafe_allow_html=True)

# Aplica imagem de fundo
set_background("plano_de_fundo.jpg")

# Título
st.title("Central de Custos | Sinalização")

# Tabelas de preços
precos_amplificador = {
    "100W": 338.19,
    "200W": 547.47,
    "Moto": 392.55
}

preco_driver = 319.81

precos_controlador = {
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

valores_modulo = {
    "Nano": 10,
    "Micro": 20,
    "D-Max": 30
}

valores_placa_led = {
    "Q-Max": 1.5,
    "OPT": 2,
    "3W": 3
}

valores_led_cor = {
    "Q-Max": {"Âmbar": 5, "Rubi": 1, "Blue": 1.5, "White": 3},
    "OPT": {"Âmbar": 5, "Rubi": 1, "Blue": 1.5, "White": 3},
    "3W": {"Âmbar": 5, "Rubi": 1, "Blue": 1.5, "White": 3}
}

# Entradas principais
amplificador = st.selectbox("Escolha o amplificador:", list(precos_amplificador.keys()))

if amplificador == "100W":
    qtd_driver = st.selectbox("Quantidade de drivers:", [0, 1])
    controlador_tipo = st.selectbox("Escolha o tipo de controlador:", list(precos_controlador.keys()))
elif amplificador == "200W":
    qtd_driver = st.selectbox("Quantidade de drivers:", [0, 2])
    controlador_tipo = st.selectbox("Escolha o tipo de controlador:", list(precos_controlador.keys()))
else:
    qtd_driver = 0
    controlador_tipo = None

# Nova estrutura de módulos auxiliares
st.markdown("### Módulo Auxiliar")
tipo_modulo = st.selectbox("Tipo de módulo:", list(valores_modulo.keys()))
tipo_led = st.selectbox("Tipo de LED:", list(valores_placa_led.keys()))
cor_led = st.selectbox("Cor do LED:", list(valores_led_cor[tipo_led].keys()))
qtd_leds = st.number_input("Quantidade de LEDs:", min_value=0, step=1)

# Cálculo do custo total
total = precos_amplificador[amplificador]
total += qtd_driver * preco_driver
if controlador_tipo:
    total += precos_controlador[controlador_tipo]

total += valores_modulo[tipo_modulo]
total += valores_placa_led[tipo_led]
total += valores_led_cor[tipo_led][cor_led] * qtd_leds

# Resultado final
st.markdown("---")
st.subheader(f"💰 Custo Estimado: R$ {total:.2f}")
