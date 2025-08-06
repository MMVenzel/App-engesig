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
qtd_modelos_modulos = st.number_input("Quantos modelos de módulos deseja adicionar?", min_value=0, step=1, value=0)
valores_modulos = []
for i in range(qtd_modelos_modulos):
    with st.expander(f"Modelo de Módulo #{i+1}"):
        tipo_modulo = st.selectbox(f"Tipo de módulo #{i+1}:", ["Nano", "Micro", "D-Max"], key=f"tipo_modulo_{i}")
        qtd_mod = st.number_input(f"Quantidade de módulos do tipo #{i+1}", min_value=1, step=1, value=1, key=f"qtd_modulo_{i}")

        tipos_led_disponiveis = list(precos_tipo_led_config[tipo_modulo].keys())
        tipo_led = st.selectbox(f"Tipo de LED #{i+1}:", tipos_led_disponiveis, key=f"tipo_led_{i}")
        max_cores = limite_cores.get((tipo_modulo, tipo_led), 3)

        col1, col2, col3 = st.columns(3)
        with col1: usar_amber = st.checkbox("Usar Amber", key=f"amber_{i}")
        with col2: usar_red = st.checkbox("Usar Red", key=f"red_{i}")
        with col3: usar_blue = st.checkbox("Usar Blue", key=f"blue_{i}")
        usar_white = st.checkbox("Usar White", key=f"white_{i}")

        cores_escolhidas = [cor for cor, usar in zip(["Amber", "Red", "Blue", "White"], [usar_amber, usar_red, usar_blue, usar_white]) if usar]
        qtd_leds_por_cor = {}

        if len(cores_escolhidas) > max_cores:
            st.error(f"⚠️ Este tipo de módulo com LED '{tipo_led}' permite no máximo {max_cores} cores.")
            continue

        for cor in cores_escolhidas:
            limite = 18
            if tipo_modulo == "Micro" and tipo_led == "3W":
                if len(cores_escolhidas) == 1:
                    limite = 9
                elif len(cores_escolhidas) == 2:
                    if cores_escolhidas.index(cor) == 0:
                        limite = 4
                    else:
                        limite = 3
                elif len(cores_escolhidas) == 3:
                    limite = 3
            elif tipo_modulo == "D-Max" and tipo_led == "3W":
                if len(cores_escolhidas) == 1:
                    limite = 18
                elif len(cores_escolhidas) in [2, 3]:
                    limite = 6
            elif tipo_modulo == "D-Max" and tipo_led == "OPT":
                if len(cores_escolhidas) == 1:
                    limite = 12
                elif len(cores_escolhidas) == 2:
                    limite = 6
            elif tipo_modulo == "D-Max" and tipo_led == "Q-MAX":
                if len(cores_escolhidas) == 1:
                    limite = 4
            elif tipo_modulo == "Micro" and tipo_led in ["OPT", "Q-MAX"]:
                limite = 3
            elif tipo_modulo == "Nano" and tipo_led == "3W":
                limite = 9 if len(cores_escolhidas) == 1 else 3

            qtd = st.number_input(f"Quantidade de LEDs {cor} (máx {limite})", min_value=0, max_value=limite, step=1, key=f"qtd_{cor}_{i}")
            qtd_leds_por_cor[cor] = qtd

        config_led = ["Single", "Dual", "Tri"][len(cores_escolhidas)-1] if cores_escolhidas else "Single"
        preco_led_config = precos_tipo_led_config[tipo_modulo][tipo_led].get(config_led, 0)
        valor_modulo_led = precos_modulo[tipo_modulo] + preco_led_config

        for cor, qtd in qtd_leds_por_cor.items():
            cor_led_price = precos_cor_led[tipo_led][cor]
            valor_modulo_led += qtd * cor_led_price

        valores_modulos.append(valor_modulo_led * qtd_mod)

# --- SINALIZADOR DE TETO ---
st.markdown("### 🚨 Sinalizador de Teto")
sinalizador_tipo = st.selectbox("Escolha o sinalizador de teto:", list(precos_sinalizador_teto.keys()))

valor_total_sinalizador = precos_sinalizador_teto.get(sinalizador_tipo, 0)
valor_total_sinalizador_modulos = 0

if sinalizador_tipo != "Nenhum":
    sinalizador_tipo_simples = sinalizador_tipo
    
    tipo_led_sinalizador = st.selectbox("Tipo de LED:", ["3W", "OPT", "Q-MAX"])
    max_cores_sinalizador = limite_cores.get(("Sinalizador", tipo_led_sinalizador), 1)

    st.markdown("---")
    st.subheader("Configurar Módulos por Cor")

    # Módulos configurados por cor (nova lógica)
    cores_disponiveis = ["Amber", "Red", "Blue", "White"]
    cores_escolhidas_s = []
    
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    with col_c1: usar_amber_s = st.checkbox("Usar Amber", key="amber_s")
    with col_c2: usar_red_s = st.checkbox("Usar Red", key="red_s")
    with col_c3: usar_blue_s = st.checkbox("Usar Blue", key="blue_s")
    with col_c4: usar_white_s = st.checkbox("Usar White", key="white_s")

    cores_escolhidas_s = [cor for cor, usar in zip(cores_disponiveis, [usar_amber_s, usar_red_s, usar_blue_s, usar_white_s]) if usar]

    if len(cores_escolhidas_s) > max_cores_sinalizador:
        st.error(f"⚠️ Este tipo de módulo com LED '{tipo_led_sinalizador}' permite no máximo {max_cores_sinalizador} cores.")
    else:
        for cor in cores_escolhidas_s:
            
            # A lógica de limite por tipo de LED e número de cores é mantida aqui
            limite_s = 18
            if tipo_led_sinalizador == "3W":
                if len(cores_escolhidas_s) == 1:
                    limite_s = 9
                elif len(cores_escolhidas_s) == 2:
                    limite_s = 3
                elif len(cores_escolhidas_s) == 3:
                    limite_s = 3
            else: # OPT e Q-MAX
                limite_s = 3

            qtd_s = st.number_input(f"Quantos módulos de LED {cor}?", min_value=0, step=1, key=f"qtd_s_mod_{cor}")
            
            # Cálculo do custo total para essa cor
            preco_led_config_s = precos_tipo_led_config["Sinalizador"][tipo_led_sinalizador].get("Single", 0)
            valor_por_modulo_s = precos_modulo["Sinalizador"] + preco_led_config_s
            valor_por_modulo_s += precos_cor_led[tipo_led_sinalizador][cor] * limite_s # Ajustando para o limite de LEDs por cor
            valor_por_modulo_s += precos_kit_sinalizador.get(sinalizador_tipo_simples, 0)
            
            valor_total_sinalizador_modulos += valor_por_modulo_s * qtd_s


valor_total_sinalizador += valor_total_sinalizador_modulos


# --- CÁLCULO FINAL ---
valor_amplificador = precos_amplificador[amplificador]
valor_driver = qtd_driver * preco_driver
valor_controlador = precos_controlador[controlador_tipo]
valor_total_modulos = sum(valores_modulos)
total = valor_amplificador + valor_driver + valor_controlador + valor_total_modulos + valor_total_sinalizador
st.subheader(f"💵 Custo Estimado: R$ {total:.2f}")

# --- GRÁFICO (Seção Corrigida) ---
buf = io.BytesIO()
if total > 0:
    labels, values, colors, text_colors = [], [], [], []
    if valor_amplificador: labels.append("Amplificador"); values.append(valor_amplificador); colors.append('#e50914'); text_colors.append("white")
    if valor_driver: labels.append("Driver"); values.append(valor_driver); colors.append('#404040'); text_colors.append("white")
    if valor_controlador: labels.append("Controlador"); values.append(valor_controlador); colors.append('#bfbfbf'); text_colors.append("white")
    if valor_total_modulos: labels.append("Módulos Aux."); values.append(valor_total_modulos); colors.append('#ffffff'); text_colors.append("black")
    if valor_total_sinalizador: labels.append("Sinalizador de Teto"); values.append(valor_total_sinalizador); colors.append('#00bfff'); text_colors.append("white")

    fig, ax = plt.subplots(figsize=(3.2, 3.2), facecolor='none')
    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, textprops={'fontsize': 9})
    for i, text in enumerate(texts): text.set_color("white")
    for i, autotext in enumerate(autotexts): autotext.set_color(text_colors[i])
    for w in wedges:
        w.set_edgecolor("black")
        w.set_linewidth(1.5)
    ax.axis('equal')
    
    plt.tight_layout()
    fig.patch.set_alpha(0)
    fig.savefig(buf, format="png", transparent=True, bbox_inches='tight')
    buf.seek(0)

    img_base64 = base64.b64encode(buf.getvalue()).decode()
    st.markdown(f"""
        <img class="grafico-fixo" src="data:image/png;base64,{img_base64}">
    """, unsafe_allow_html=True)

# --- BOTÕES FLUTUANTES: GERAR E BAIXAR PDF ---
if total > 0:
    if 'pdf_gerado' not in st.session_state:
        st.session_state.pdf_gerado = False
    if 'pdf_bytes' not in st.session_state:
        st.session_state.pdf_bytes = None

    if not st.session_state.pdf_gerado:
        st.markdown('<div class="botao-pdf-flutuante">', unsafe_allow_html=True)
        if st.button("📄 Gerar Relatório"):
            pdf_bytes = gerar_pdf(
                amplificador, valor_amplificador, qtd_driver, valor_driver,
                controlador_tipo, valor_controlador, valores_modulos,
                valor_total_modulos, sinalizador_tipo, valor_total_sinalizador,
                total, buf
            )
            st.session_state.pdf_bytes = pdf_bytes
            st.session_state.pdf_gerado = True
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.pdf_gerado and st.session_state.pdf_bytes:
        st.markdown('<div class="download-pdf-flutuante">', unsafe_allow_html=True)
        st.download_button(
            label="📥 Baixar PDF",
            data=st.session_state.pdf_bytes,
            file_name="relatorio_custos.pdf",
            mime='application/pdf',
            key="download_pdf_botao"
        )
        st.markdown('</div>', unsafe_allow_html=True)


# --- RODAPÉ & LOGO FIXA ---
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
