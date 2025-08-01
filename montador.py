import streamlit as st
from PIL import Image
import base64

# Função para aplicar imagem de fundo
def set_background(image_file):
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');

    .stApp {{
        background-image: url("data:image/jpg;base64,{base64.b64encode(open(image_file, "rb").read()).decode()}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: white;
    }}

    h1 {{
        font-family: 'Montserrat', sans-serif !important;
    }}

    header {{
        visibility: hidden;
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

# Preços
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

# Tipo de módulo
tipos_modulo = {
    "Nenhum": 0,
    "Nano": 10,
    "Micro": 20,
    "D-Max": 30
}

# Custo da placa por tipo de LED
tipos_led = {
    "Q-Max": 1.50,
    "OPT": 2.00,
    "3W": 3.00
}

# Custo por cor de LED (iguais por enquanto para todos os tipos)
cores_led = {
    "Ambar": 5.00,
    "Rubi": 1.00,
    "Blue": 1.50,
    "White": 3.00
}

# Entradas de amplificador, driver e controlador
amplificador = st.selectbox("Escolha o amplificador:", list(precos_amplificador.keys()))

if amplificador == "100W":
    qtd_driver = st.selectbox("Quantidade de drivers:", [0, 1])
elif amplificador == "200W":
    qtd_driver = st.selectbox("Quantidade de drivers:", [0, 2])
elif amplificador == "Moto":
    qtd_driver = 0
else:
    qtd_driver = st.selectbox("Quantidade de drivers:", [0, 1, 2])

controlador_tipo = st.selectbox("Escolha o tipo de controlador:", list(precos_controlador.keys()))

# Entradas para módulo
tipo_modulo = st.selectbox("Escolha o tipo de módulo:", list(tipos_modulo.keys()))
if tipo_modulo != "Nenhum":
    tipo_led = st.selectbox("Escolha o tipo de LED:", list(tipos_led.keys()))
    cor_led = st.selectbox("Escolha a cor do LED:", list(cores_led.keys()))
    qtd_leds = st.number_input("Quantidade de LEDs:", min_value=0, step=1)
else:
    tipo_led = None
    cor_led = None
    qtd_leds = 0

# Cálculo total

# Módulo + placa + leds
if tipo_modulo == "Nenhum":
    custo_modulo = 0
else:
    custo_modulo = tipos_modulo[tipo_modulo] + tipos_led[tipo_led] + (cores_led[cor_led] * qtd_leds)

# Soma geral
custo_total = precos_amplificador[amplificador] + (qtd_driver * preco_driver) + precos_controlador[controlador_tipo] + custo_modulo

# Resultado
st.markdown("---")
st.subheader(f"💰 Custo Estimado: R$ {custo_total:.2f}")

