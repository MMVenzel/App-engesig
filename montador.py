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
    /* Estilo para o botão de PDF flutuante */
    .botao-pdf-flutuante {
        position: fixed;
        bottom: 30px; /* Distância do fundo */
        right: 30px;  /* Distância da direita */
        z-index: 10001; /* Garante que fique na camada de cima */
    }
    </style>
""", unsafe_allow_html=True)

# --- DADOS ---
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
        "Q-MAX": {"Single": 7.3},
    },
    "D-Max": {
        "3W": {"Single": 15.2, "Dual": 18.94, "Tri": 23.51},
        "OPT": {"Single": 15.31},
        "Q-MAX": {"Single": 9.1},
    }
}
precos_cor_led = {
    "3W": {"Ambar": 5.79, "Rubi": 3.58, "Blue": 3.58, "White": 3.58},
    "OPT": {"Ambar": 1.36, "Rubi": 0.86, "Blue": 1.00, "White": 1.60},
    "Q-MAX": {"Ambar": 1.36, "Rubi": 0.86, "Blue": 1.00, "White": 1.60}
}
limite_cores = {
    ("Nano", "3W"): 3,
    ("Micro", "3W"): 3,
    ("Micro", "OPT"): 2,
    ("Micro", "Q-MAX"): 1,
    ("D-Max", "3W"): 3,
    ("D-Max", "OPT"): 2,
    ("D-Max", "Q-MAX"): 1
}

# --- FUNÇÃO PDF ---
def gerar_pdf(amplificador, valor_amplificador, qtd_driver, valor_driver,
              controlador_tipo, valor_controlador, valores_modulos,
              valor_total_modulos, total, img_bytes):

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
qtd_modulos = st.number_input("Quantas configurações diferentes de módulo auxiliar deseja adicionar?", min_value=0, step=1, value=0)
valores_modulos = []

for i in range(qtd_modulos):
    with st.expander(f"Módulo #{i+1}"):
        tipo_modulo = st.selectbox(f"Tipo de módulo #{i+1}:", list(precos_modulo.keys()), key=f"tipo_modulo_{i}")
        qtd_mod = st.number_input(f"Quantidade de módulos do tipo #{i+1}", min_value=1, step=1, value=1, key=f"qtd_modulo_{i}")
        if tipo_modulo == "Nenhum":
            continue

        tipos_led_disponiveis = list(precos_tipo_led_config[tipo_modulo].keys())
        tipo_led = st.selectbox(f"Tipo de LED #{i+1}:", tipos_led_disponiveis, key=f"tipo_led_{i}")
        max_cores = limite_cores.get((tipo_modulo, tipo_led), 3)

        col1, col2, col3 = st.columns(3)
        with col1: usar_ambar = st.checkbox("Usar Ambar", key=f"ambar_{i}")
        with col2: usar_rubi = st.checkbox("Usar Rubi", key=f"rubi_{i}")
        with col3: usar_blue = st.checkbox("Usar Blue", key=f"blue_{i}")
        usar_white = st.checkbox("Usar White", key=f"white_{i}")

        cores_escolhidas = [cor for cor, usar in zip(["Ambar", "Rubi", "Blue", "White"], [usar_ambar, usar_rubi, usar_blue, usar_white]) if usar]
        qtd_leds_por_cor = {}

        if len(cores_escolhidas) > max_cores:
            st.error(f"⚠️ Este tipo de módulo com LED '{tipo_led}' permite no máximo {max_cores} cores.")
            continue

        for cor in cores_escolhidas:
            if tipo_modulo == "Nano" and tipo_led == "3W":
                limite = 9 if len(cores_escolhidas) == 1 else 3
            else:
                limite = 3
            qtd = st.number_input(f"Quantidade de LEDs {cor} (máx {limite})", min_value=0, max_value=limite, step=1, key=f"qtd_{cor}_{i}")
            qtd_leds_por_cor[cor] = qtd

        config_led = ["Single", "Dual", "Tri"][len(cores_escolhidas)-1] if cores_escolhidas else "Single"
        preco_led_config = precos_tipo_led_config[tipo_modulo][tipo_led].get(config_led, 0)
        valor_modulo_led = precos_modulo[tipo_modulo] + preco_led_config

        for cor, qtd in qtd_leds_por_cor.items():
            cor_led_price = precos_cor_led[tipo_led][cor]
            valor_modulo_led += qtd * cor_led_price

        valores_modulos.append(valor_modulo_led * qtd_mod)

# --- CÁLCULO FINAL ---
valor_amplificador = precos_amplificador[amplificador]
valor_driver = qtd_driver * preco_driver
valor_controlador = precos_controlador[controlador_tipo]
valor_total_modulos = sum(valores_modulos)
total = valor_amplificador + valor_driver + valor_controlador + valor_total_modulos
st.subheader(f"💵 Custo Estimado: R$ {total:.2f}")

# --- GRÁFICO ---
buf = io.BytesIO() # Inicializa o buffer aqui para garantir que ele sempre exista
if total > 0:
    labels, values, colors, text_colors = [], [], [], []
    if valor_amplificador: labels.append("Amplificador"); values.append(valor_amplificador); colors.append('#e50914'); text_colors.append("white")
    if valor_driver: labels.append("Driver"); values.append(valor_driver); colors.append('#404040'); text_colors.append("white")
    if valor_controlador: labels.append("Controlador"); values.append(valor_controlador); colors.append('#bfbfbf'); text_colors.append("white")
    if valor_total_modulos: labels.append("Módulos Aux."); values.append(valor_total_modulos); colors.append('#ffffff'); text_colors.append("black")

    fig, ax = plt.subplots(figsize=(3.2, 3.2), facecolor='none')
    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, textprops={'fontsize': 9})
    for i, text in enumerate(texts): text.set_color("white")
    for i, autotext in enumerate(autotexts): autotext.set_color(text_colors[i])
    for w in wedges:
        w.set_edgecolor("black")
        w.set_linewidth(1.5)
    ax.axis('equal')
    fig.patch.set_alpha(0)
    
    # Salva a figura no buffer
    fig.savefig(buf, format="png", transparent=True, bbox_inches='tight', pad_inches=0.1)
    buf.seek(0)
    
    img_base64 = base64.b64encode(buf.getvalue()).decode()
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


# --- BOTÃO PARA GERAR E BAIXAR PDF (FLUTUANTE) ---
if total > 0:
    # Envelopa os botões na div flutuante
    st.markdown('<div class="botao-pdf-flutuante">', unsafe_allow_html=True)

    # O botão de download só é gerado DEPOIS que o botão de gerar é clicado.
    # Para manter o botão de download no mesmo lugar, criamos um estado de sessão.
    if 'pdf_gerado' not in st.session_state:
        st.session_state.pdf_gerado = False
    
    if 'pdf_bytes' not in st.session_state:
        st.session_state.pdf_bytes = None

    if st.button("📄 Gerar Relatório"):
        pdf_bytes = gerar_pdf(
            amplificador, valor_amplificador, qtd_driver, valor_driver,
            controlador_tipo, valor_controlador, valores_modulos,
            valor_total_modulos, total, buf
        )
        st.session_state.pdf_bytes = pdf_bytes
        st.session_state.pdf_gerado = True
        st.rerun() # Força o rerom para mostrar o botão de download imediatamente

    if st.session_state.pdf_gerado:
        st.download_button(
            label="📥 Baixar PDF",
            data=st.session_state.pdf_bytes,
            file_name="relatorio_custos.pdf",
            mime='application/pdf'
        )
        # Reseta o estado para o botão de "Gerar" reaparecer na próxima interação
        st.session_state.pdf_gerado = False

    st.markdown('</div>', unsafe_allow_html=True)


# --- RODAPÉ E LOGO ---
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
