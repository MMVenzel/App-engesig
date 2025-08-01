import streamlit as st
from PIL import Image
import base64
from pathlib import Path
import matplotlib.pyplot as plt
import io

# Configura a aba do navegador
st.set_page_config(
    page_title="Engesig | Central de Custos",
    page_icon="logo_engesig.ico"
)

# Estilo escuro fixo (sem imagem de fundo)
st.markdown("""
    <style>
    :root { color-scheme: dark; }

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

    .stSelectbox div[data-baseweb="select"] * {
        color: white !important;
        background-color: rgba(30, 30, 30, 0.7) !important;
    }

    div[data-baseweb="popover"] * {
        color: white !important;
        background-color: #333 !important;
    }

    .stSelectbox input, input[type="number"] {
        color: white !important;
        background-color: rgba(30, 30, 30, 0.7) !important;
    }

    header { visibility: hidden; }

    [data-testid="stHeader"] {
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
precos_modulo = {"Nenhum": 0, "Nano": 39.67, "Micro": 25.69, "D-Max": 28.17}
precos_tipo_led_config = {
    "Nano": {"3W": {"Single": 20.90, "Dual": 31.27, "Tri": 33.51}},
    "Micro": {
        "3W": {"Single": 14.89, "Dual": 19.09, "Tri": 20.56},
        "OPT": {"Single": 13.97},
        "Q-MAX": {"Single": 7.30},
    },
    "D-Max": {
        "3W": {"Single": 15.20, "Dual": 18.94, "Tri": 23.51},
        "OPT": {"Single": 15.31},
        "Q-MAX": {"Single": 9.10},
    }
}
precos_cor_led_3w = {"Ambar": 5.79, "Rubi": 3.58, "Blue": 3.58, "White": 3.58}
precos_cor_led_opt_qmax = {"Ambar": 1.36, "Rubi": 0.86, "Blue": 1.00, "White": 1.60}

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

# LED
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
valor_amplificador = precos_amplificador[amplificador]
valor_driver = qtd_driver * preco_driver
valor_controlador = precos_controlador[controlador_tipo]
valor_modulo_led = 0

if tipo_modulo != "Nenhum" and tipo_led:
    preco_led_config = precos_tipo_led_config[tipo_modulo][tipo_led].get(config_led, precos_tipo_led_config[tipo_modulo][tipo_led].get("Single", 0))
    valor_modulo_led = precos_modulo[tipo_modulo] + preco_led_config
    tabela_custos_led = precos_cor_led_3w if tipo_led == "3W" else precos_cor_led_opt_qmax
    for cor, qtd in qtd_leds_por_cor.items():
        valor_modulo_led += qtd * tabela_custos_led.get(cor, 0)

total = valor_amplificador + valor_driver + valor_controlador + valor_modulo_led
st.subheader(f"💵 Custo Estimado: R$ {total:.2f}")

# Gráfico
if total > 0:
    labels = ['Amplificador', 'Driver', 'Controlador', 'Módulos Aux.']
    values = [valor_amplificador, valor_driver, valor_controlador, valor_modulo_led]
    colors = ['#e50914', '#404040', '#bfbfbf', '#ffffff']
    text_colors = ['white', 'white', 'white', 'black']

    fig, ax = plt.subplots(figsize=(3.2, 3.2), facecolor='none')
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'fontsize': 9}
    )

    for i, text in enumerate(texts):
        text.set_color("white")
        text.set_fontsize(9)
    for i, autotext in enumerate(autotexts):
        autotext.set_color(text_colors[i])

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
