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

precos_tipo_led_config = {
    "Nano": {
        "3W": {"Single": 20.90, "Dual": 31.27, "Tri": 33.51}
    },
    "Micro": {
        "3W": {"Single": 25, "Dual": 35, "Tri": 40},
        "Q-Max": {"Single": 22, "Dual": 30, "Tri": 34},
        "OPT": {"Single": 21, "Dual": 29, "Tri": 33},
    },
    "D-Max": {
        "3W": {"Single": 27, "Dual": 37, "Tri": 43},
        "Q-Max": {"Single": 23, "Dual": 32, "Tri": 36},
        "OPT": {"Single": 24, "Dual": 34, "Tri": 39},
    }
}

precos_cor_led = {
    "Ambar": 5,
    "Rubi": 1,
    "Blue": 1.5,
    "White": 3
}

# Entradas do usuário
amplificador = st.selectbox("Escolha o amplificador:", list(precos_amplificador.keys()))

qtd_driver = 0
if amplificador in ["100W", "200W"]:
    driver_incluso = st.selectbox("Acompanha driver?", ["Não", "Sim"])
    if driver_incluso == "Sim":
        qtd_driver = 1 if amplificador == "100W" else 2

controlador_tipo = st.selectbox("Escolha o tipo de controlador:", list(precos_controlador.keys()))

st.markdown("### Módulo Auxiliar")

# Configuração de módulo e LED
tipo_modulo = st.selectbox("Tipo de módulo:", list(precos_modulo.keys()))

if tipo_modulo == "Nenhum":
    tipo_led = None
    qtd_leds_por_cor = {}
    config_led = None
else:
    tipos_led_disponiveis = list(precos_tipo_led_config[tipo_modulo].keys())
    tipo_led = st.selectbox("Tipo de LED:", tipos_led_disponiveis)

    col1, col2, col3 = st.columns(3)
    with col1:
        usar_ambar = st.checkbox("Usar Ambar")
    with col2:
        usar_rubi = st.checkbox("Usar Rubi")
    with col3:
        usar_blue = st.checkbox("Usar Blue")
    usar_white = st.checkbox("Usar White")

    qtd_leds_por_cor = {}
    cores_escolhidas = []
    for cor, usar in zip(["Ambar", "Rubi", "Blue", "White"], [usar_ambar, usar_rubi, usar_blue, usar_white]):
        if usar:
            cores_escolhidas.append(cor)
            qtd = st.number_input(f"Quantidade de LEDs {cor}", min_value=0, step=1, key=f"qtd_{cor}")
            qtd_leds_por_cor[cor] = qtd

    num_cores = len(cores_escolhidas)
    if num_cores == 1:
        config_led = "Single"
    elif num_cores == 2:
        config_led = "Dual"
    elif num_cores >= 3:
        config_led = "Tri"
    else:
        config_led = None

# Cálculo do custo total
total = precos_amplificador[amplificador] + (qtd_driver * preco_driver) + precos_controlador[controlador_tipo]

if tipo_modulo != "Nenhum" and tipo_led and config_led:
    preco_led_config = precos_tipo_led_config[tipo_modulo][tipo_led][config_led]
    total += precos_modulo[tipo_modulo] + preco_led_config
    for cor, qtd in qtd_leds_por_cor.items():
        total += qtd * precos_cor_led[cor]

st.subheader(f"\U0001F4B5 Custo Estimado: R$ {total:.2f}")

# Rodapé
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
logo_path = Path("logo.png")
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
