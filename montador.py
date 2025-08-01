import streamlit as st
from PIL import Image
import base64
from pathlib import Path
import matplotlib.pyplot as plt
import io

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
        background-color: rgba(30, 30, 30, 0.7) !important;
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
        background-color: rgba(30, 30, 30, 0.7) !important;
    }}

    .css-1cpxqw2, .css-1d391kg {{
        color: white !important;
    }}

    header {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# Aplica fundo
set_background("plano_de_fundo.jpg")

# Tipografia moderna e animação de resposta tátil
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', sans-serif;
        font-size: 16px;
    }
    .stApp {
        padding: 2rem;
    }

    div[data-baseweb="select"]:focus-within {
        border: 2px solid #00FFAA !important;
        animation: pulse 0.3s ease-in-out;
        border-radius: 8px;
    }

    @keyframes pulse {
        0%   { box-shadow: 0 0 0px #00FFAA; }
        50%  { box-shadow: 0 0 8px #00FFAA; }
        100% { box-shadow: 0 0 0px #00FFAA; }
    }

    input:focus, select:focus, textarea:focus {
        outline: none;
        box-shadow: 0 0 10px #00FFAA;
    }
    </style>
""", unsafe_allow_html=True)

# Dados
precos_amplificador = {"Nenhum": 0, "100W": 338.19, "200W": 547.47, "Moto": 392.55}
preco_driver = 319.81
precos_controlador = {
    "Nenhum": 0, "Micro 3B Moto": 90.98, "Micro 3B C/ Mic": 1, "Micro 4B S/ Mic": 1,
    "Micro 4B com Mic": 137.32, "Handheld 9B Magnético": 216.44, "Handheld 15B": 194.57,
    "Handheld 18B": 1, "Controlador Fixo 15B": 1, "Controlador Fixo 17B": 1
}
precos_modulo = {"Nenhum": 0, "Nano": 39.67, "Micro": 25.69, "D-Max": 28.67}
precos_tipo_led_config = {
    "Nano": {"3W": {"Single": 20.90, "Dual": 31.27, "Tri": 33.51}},
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
precos_cor_led = {"Ambar": 5, "Rubi": 1, "Blue": 1.5, "White": 3}

# Título
st.title("Central de Custos | Sinalização")

# Entradas
amplificador = st.selectbox("Escolha o amplificador:", list(precos_amplificador.keys()))
qtd_driver = 0
if amplificador in ["100W", "200W"]:
    if st.selectbox("Acompanha driver?", ["Não", "Sim"]) == "Sim":
        qtd_driver = 1 if amplificador == "100W" else 2

controlador_tipo = st.selectbox("Escolha o tipo de controlador:", list(precos_controlador.keys()))
st.markdown("### 🔧 Módulo Auxiliar")
tipo_modulo = st.selectbox("Tipo de módulo:", list(precos_modulo.keys()))

tipo_led = None
qtd_leds_por_cor = {}
config_led = None

if tipo_modulo != "Nenhum":
    tipos_led_disponiveis = list(precos_tipo_led_config[tipo_modulo].keys())
    tipo_led = st.selectbox("Tipo de LED:", tipos_led_disponiveis)

    col1, col2, col3 = st.columns(3)
    with col1: usar_ambar = st.checkbox("Usar Ambar")
    with col2: usar_rubi = st.checkbox("Usar Rubi")
    with col3: usar_blue = st.checkbox("Usar Blue")
    usar_white = st.checkbox("Usar White")

    cores_escolhidas = []
    for cor, usar in zip(["Ambar", "Rubi", "Blue", "White"], [usar_ambar, usar_rubi, usar_blue, usar_white]):
        if usar:
            cores_escolhidas.append(cor)
            qtd = st.number_input(f"Quantidade de LEDs {cor}", min_value=0, step=1, key=f"qtd_{cor}")
            qtd_leds_por_cor[cor] = qtd

    if len(cores_escolhidas) == 1:
        config_led = "Single"
    elif len(cores_escolhidas) == 2:
        config_led = "Dual"
    elif len(cores_escolhidas) >= 3:
        config_led = "Tri"

# Cálculo
total = 0
valor_amplificador = precos_amplificador[amplificador]
valor_driver = qtd_driver * preco_driver
valor_controlador = precos_controlador[controlador_tipo]
valor_modulo_led = 0

if tipo_modulo != "Nenhum" and tipo_led and config_led:
    preco_led_config = precos_tipo_led_config[tipo_modulo][tipo_led][config_led]
    valor_modulo_led = precos_modulo[tipo_modulo] + preco_led_config
    for cor, qtd in qtd_leds_por_cor.items():
        valor_modulo_led += qtd * precos_cor_led[cor]

total = valor_amplificador + valor_driver + valor_controlador + valor_modulo_led
st.subheader(f"💵 Custo Estimado: R$ {total:.2f}")

# Gráfico flutuante
if total > 0:
    labels = ['Amplificador', 'Driver', 'Controlador', 'Módulo + LED']
    values = [valor_amplificador, valor_driver, valor_controlador, valor_modulo_led]
    colors = ['#2E86AB', '#F28C28', '#58A55C', '#C0392B']

    fig, ax = plt.subplots(figsize=(3.2, 3.2), facecolor='none')
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'color': 'white', 'fontsize': 9}
    )
    for text in texts:
        text.set_fontsize(9)
    ax.axis('equal')
    fig.patch.set_alpha(0)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", transparent=True, bbox_inches='tight', pad_inches=0.1)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()

    st.markdown(f"""
        <style>
        .grafico-flutuante {{
            position: fixed;
            top: 290px;
            left: 30px;
            width: 300px;
            z-index: 10000;
            background: none;
        }}
        </style>
        <img class="grafico-flutuante" src="data:image/png;base64,{img_base64}">
    """, unsafe_allow_html=True)

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
