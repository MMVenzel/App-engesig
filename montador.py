import streamlit as st
from PIL import Image
import base64

# Função para aplicar imagem de fundo
def set_background(image_file):
    st.markdown("""
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .css-18ni7ap.e8zbici2 {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Aplica imagem de fundo
set_background("plano de fundo.jpg")

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
    "15B": 194.57,
    "Micro 4B c/ Mic": 137.32,
    "Handheld 9B Magnético": 216.44,
    "Micro 3B Moto": 90.98
}

preco_modulo_aux = 75

# Entradas
amplificador = st.selectbox("Escolha o amplificador:", list(precos_amplificador.keys()))

if amplificador != "Moto":
    qtd_driver = st.selectbox("Quantidade de drivers:", [0, 1, 2])
    controlador_tipo = st.selectbox("Escolha o tipo de controlador:", list(precos_controlador.keys()))
else:
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
