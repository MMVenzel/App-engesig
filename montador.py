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

    /* Cores globais */
    h1, h2, h3, h4, h5, h6, p, label, div, span {{
        color: white !important;
    }}

    /* Input geral e select */
    .stSelectbox div[data-baseweb="select"] * {{
        color: white !important;
        background-color: rgba(0, 0, 0, 0.6) !important;
    }}

    /* Dropdown aberto */
    div[data-baseweb="popover"] * {{
        color: white !important;
        background-color: #333 !important;
    }}

    /* Texto digitável dentro do select */
    .stSelectbox input {{
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

precos_modulo_aux = {
    "Micro D-Max Quantum": 1,
    "Micro D-Max OPT": 1,
    "Micro D-Max Single Color 4 Leds": 1,
    "Micro D-Max Single Color 6 Leds": 1,
    "Micro D-Max Dual Color": 1,
}
    
    

# Entradas
amplificador = st.selectbox("Escolha o amplificador:", list(precos_amplificador.keys()))

if amplificador == "100W":
    qtd_driver = st.selectbox("Quantidade de drivers:", [0, 1])
    controlador_tipo = st.selectbox("Escolha o tipo de controlador:", list(precos_controlador.keys()))
elif amplificador == "200W":
    qtd_driver = st.selectbox("Quantidade de drivers:", [0, 2])
    controlador_tipo = st.selectbox("Escolha o tipo de controlador:", list(precos_controlador.keys()))
else:  # Moto
    qtd_driver = 0
    controlador_tipo = None


quantidade_modulos = st.number_input("Quantidade de módulos auxiliares:", min_value=0, step=1)

# Cálculo
total = precos_amplificador[amplificador]
total += qtd_driver * preco_driver
if controlador_tipo:
    total += precos_controlador[controlador_tipo]
total += quantidade_modulos * preco_modulo_aux

# Resultado
st.markdown("---")
st.subheader(f"💰 Custo Estimado: R$ {total:.2f}")
