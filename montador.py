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

# --- FUNÇÃO PARA CARREGAR O CSS EXTERNO ---
def carregar_css(caminho_do_arquivo):
    """Lê um arquivo CSS e o injeta no app Streamlit."""
    try:
        with open(caminho_do_arquivo) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Arquivo de estilo '{caminho_do_arquivo}' não encontrado. Certifique-se de que ele está na mesma pasta que o script Python.")

# --- CARREGA O ESTILO DO ARQUIVO CSS ---
carregar_css("style.css")


# --- DADOS ---
precos_amplificador = {"Nenhum": 0, "100W": 338.19, "200W": 547.47, "Moto": 392.55}
preco_driver = 319.81
precos_controlador = {
    "Nenhum": 0, "Micro 3B Moto": 102.98, "Micro 3B C/ Mic": 145.50, "Micro 4B com Mic": 145.36,
    "Handheld 9B Magnético": 236.44, "Controlador Fixo 15B": 206.30, "Controlador Fixo 17B": 216.60
}
precos_modulo = {"Nenhum": 0, "Nano": 39.67, "Micro": 25.69, "D-Max": 28.17, "Sinalizador": 25.69}
precos_sinalizador_teto = {"Nenhum": 0, "Sirius": 100.00, "Brutale": 100.00}
precos_kit_sinalizador = {"Sirius": 3.00, "Brutale": 7.00}
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
    ("Nano", "3W"): 3, ("Micro", "3W"): 3, ("Micro", "OPT"): 1,
    ("Micro", "Q-MAX"): 1, ("D-Max", "3W"): 3, ("D-Max", "OPT"): 2,
    ("D-Max", "Q-MAX"): 1, ("Sinalizador", "3W"): 3, ("Sinalizador", "OPT"): 1,
    ("Sinalizador", "Q-MAX"): 1
}

# --- FUNÇÕES AUXILIARES ---
def calcular_limite_leds(tipo_modulo, tipo_led, cores_escolhidas, cor_atual):
    num_cores = len(cores_escolhidas)
    limite = 18
    if tipo_modulo == "Micro":
        if tipo_led == "3W":
            if num_cores == 1: limite = 9
            elif num_cores == 2: limite = 4 if cores_escolhidas.index(cor_atual) == 0 else 3
            elif num_cores == 3: limite = 3
        else: limite = 3
    elif tipo_modulo == "D-Max":
        if tipo_led == "3W": limite = 18 if num_cores == 1 else 6
        elif tipo_led == "OPT": limite = 12 if num_cores == 1 else 6
        elif tipo_led == "Q-MAX": limite = 4
    elif tipo_modulo == "Nano" and tipo_led == "3W": limite = 9 if num_cores == 1 else 3
    elif tipo_modulo == "Sinalizador":
        if tipo_led == "3W":
            if num_cores in [2, 3]: limite = 3
            else: limite = 9
        else: limite = 3
    return limite

def gerar_pdf(amplificador, valor_amplificador, qtd_driver, valor_driver,
              controlador_tipo, valor_controlador, valor_total_modulos,
              sinalizador_tipo, valor_total_sinalizador, total, img_bytes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="Relatório de Custo - Sinalização", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", '', 10)
    data = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.cell(0, 8, txt=f"Data de Geração: {data}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Resumo dos Componentes", ln=True, border='B')
    pdf.set_font("Arial", size=11)
    pdf.ln(4)
    pdf.cell(100, 8, txt=f"Amplificador: {amplificador}", ln=0)
    pdf.cell(0, 8, txt=f"R$ {valor_amplificador:.2f}", ln=1, align='R')
    if qtd_driver:
        pdf.cell(100, 8, txt=f"Driver(s): {qtd_driver}x", ln=0)
        pdf.cell(0, 8, txt=f"R$ {valor_driver:.2f}", ln=1, align='R')
    pdf.cell(100, 8, txt=f"Controlador: {controlador_tipo}", ln=0)
    pdf.cell(0, 8, txt=f"R$ {valor_controlador:.2f}", ln=1, align='R')
    if valor_total_modulos > 0:
        pdf.cell(100, 8, txt="Total Módulos Auxiliares:", ln=0)
        pdf.cell(0, 8, txt=f"R$ {valor_total_modulos:.2f}", ln=1, align='R')
    if valor_total_sinalizador > 0:
        pdf.cell(100, 8, txt=f"Sinalizador de Teto ({sinalizador_tipo}):", ln=0)
        pdf.cell(0, 8, txt=f"R$ {valor_total_sinalizador:.2f}", ln=1, align='R')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(100, 10, txt="CUSTO TOTAL:", ln=0)
    pdf.cell(0, 10, txt=f"R$ {total:.2f}", ln=1, align='R', border='T')
    pdf.ln(10)
    if img_bytes and img_bytes.getbuffer().nbytes > 0:
        pdf.image(img_bytes, x=pdf.get_x() + 45, w=100, type='PNG', title="Distribuição de Custos")
    return pdf.output()

# --- INTERFACE PRINCIPAL ---
st.title("Central de Custos | Sinalização")
amplificador = st.selectbox("Escolha o amplificador:", list(precos_amplificador.keys()))
qtd_driver = 0
if amplificador in ["100W", "200W"]:
    if st.selectbox("Acompanha driver?", ["Não", "Sim"]) == "Sim":
        qtd_driver = 1 if amplificador == "100W" else 2
controlador_tipo = st.selectbox("Escolha o tipo de controlador:", list(precos_controlador.keys()))

st.markdown("### 🔧 Módulos Auxiliares")
qtd_modelos_modulos = st.number_input("Quantos modelos de módulos deseja adicionar?", min_value=0, step=1, value=0, key="qtd_modelos_modulos_input")
valores_modulos = []
for i in range(qtd_modelos_modulos):
    with st.expander(f"Modelo de Módulo Auxiliar #{i+1}"):
        tipo_modulo = st.selectbox(f"Tipo de módulo #{i+1}:", ["Nano", "Micro", "D-Max"], key=f"tipo_modulo_{i}")
        qtd_mod = st.number_input(f"Quantidade de módulos do tipo #{i+1}", min_value=1, step=1, value=1, key=f"qtd_modulo_{i}")
        tipos_led_disponiveis = list(precos_tipo_led_config[tipo_modulo].keys())
        tipo_led = st.selectbox(f"Tipo de LED #{i+1}:", tipos_led_disponiveis, key=f"tipo_led_{i}")
        max_cores = limite_cores.get((tipo_modulo, tipo_led), 1)
        cols = st.columns(4)
        usar_amber = cols[0].checkbox("Amber", key=f"amber_{i}")
        usar_red = cols[1].checkbox("Red", key=f"red_{i}")
        usar_blue = cols[2].checkbox("Blue", key=f"blue_{i}")
        usar_white = cols[3].checkbox("White", key=f"white_{i}")
        cores_escolhidas = [cor for cor, usar in zip(["Amber", "Red", "Blue", "White"], [usar_amber, usar_red, usar_blue, usar_white]) if usar]
        if len(cores_escolhidas) > max_cores:
            st.error(f"⚠️ Este tipo de módulo com LED '{tipo_led}' permite no máximo {max_cores} cor(es).")
            continue
        qtd_leds_por_cor = {}
        for cor in cores_escolhidas:
            limite = calcular_limite_leds(tipo_modulo, tipo_led, cores_escolhidas, cor)
            qtd = st.number_input(f"Quantidade de LEDs {cor} (máx {limite})", min_value=0, max_value=limite, step=1, key=f"qtd_{cor}_{i}")
            qtd_leds_por_cor[cor] = qtd
        config_led = "Single"
        if len(cores_escolhidas) > 0: config_led = ["Single", "Dual", "Tri"][len(cores_escolhidas)-1]
        preco_led_config = precos_tipo_led_config[tipo_modulo][tipo_led].get(config_led, 0)
        valor_modulo_unidade = precos_modulo[tipo_modulo] + preco_led_config
        for cor, qtd in qtd_leds_por_cor.items(): valor_modulo_unidade += qtd * precos_cor_led[tipo_led][cor]
        valores_modulos.append(valor_modulo_unidade * qtd_mod)

st.markdown("### 🚨 Sinalizador de Teto")
sinalizador_tipo = st.selectbox("Escolha o sinalizador de teto:", list(precos_sinalizador_teto.keys()), key="sinalizador_tipo_select")
valor_total_sinalizador_modulos = 0
if sinalizador_tipo != "Nenhum":
    valor_base_sinalizador = precos_sinalizador_teto.get(sinalizador_tipo, 0) + precos_kit_sinalizador.get(sinalizador_tipo, 0)
    tipo_led_sinalizador = st.selectbox("Tipo de LED:", ["3W", "OPT", "Q-MAX"], key="sinalizador_led_type")
    qtd_modelos_sinalizador = st.number_input("Quantos modelos de módulos para o sinalizador?", min_value=0, step=1, value=0, key="qtd_modelos_sinalizador")
    for j in range(qtd_modelos_sinalizador):
        with st.expander(f"Modelo de Módulo Sinalizador #{j+1}"):
            qtd_mod_sinalizador = st.number_input(f"Quantidade de módulos do modelo #{j+1}", min_value=1, step=1, value=1, key=f"qtd_mod_sinalizador_{j}")
            max_cores_sinalizador = limite_cores.get(("Sinalizador", tipo_led_sinalizador), 1)
            cols_s = st.columns(4)
            usar_amber_s = cols_s[0].checkbox("Amber", key=f"amber_s_{j}")
            usar_red_s = cols_s[1].checkbox("Red", key=f"red_s_{j}")
            usar_blue_s = cols_s[2].checkbox("Blue", key=f"blue_s_{j}")
            usar_white_s = cols_s[3].checkbox("White", key=f"white_s_{j}")
            cores_escolhidas_s = [cor for cor, usar in zip(["Amber", "Red", "Blue", "White"], [usar_amber_s, usar_red_s, usar_blue_s, usar_white_s]) if usar]
            if len(cores_escolhidas_s) > max_cores_sinalizador:
                st.error(f"⚠️ Este tipo de módulo com LED '{tipo_led_sinalizador}' permite no máximo {max_cores_sinalizador} cor(es).")
                continue
            qtd_leds_por_cor_s = {}
            for cor_s in cores_escolhidas_s:
                limite_s = calcular_limite_leds("Sinalizador", tipo_led_sinalizador, cores_escolhidas_s, cor_s)
                qtd_s = st.number_input(f"Quantidade de LEDs {cor_s} (máx {limite_s})", min_value=0, max_value=limite_s, step=1, key=f"qtd_s_{cor_s}_{j}")
                qtd_leds_por_cor_s[cor_s] = qtd_s
            config_led_s = "Single"
            if len(cores_escolhidas_s) > 0: config_led_s = ["Single", "Dual", "Tri"][len(cores_escolhidas_s)-1]
            preco_led_config_s = precos_tipo_led_config["Sinalizador"][tipo_led_sinalizador].get(config_led_s, 0)
            valor_por_modelo_s = precos_modulo["Sinalizador"] + preco_led_config_s
            for cor, qtd in qtd_leds_por_cor_s.items(): valor_por_modelo_s += qtd * precos_cor_led[tipo_led_sinalizador][cor]
            valor_total_sinalizador_modulos += valor_por_modelo_s * qtd_mod_sinalizador
    valor_total_sinalizador = valor_base_sinalizador + valor_total_sinalizador_modulos
else:
    valor_total_sinalizador = 0

# --- CÁLCULO FINAL E BOTÕES ---
valor_amplificador = precos_amplificador[amplificador]
valor_driver = qtd_driver * preco_driver
valor_controlador = precos_controlador[controlador_tipo]
valor_total_modulos = sum(valores_modulos)
total = valor_amplificador + valor_driver + valor_controlador + valor_total_modulos + valor_total_sinalizador
st.subheader(f"💵 Custo Estimado: R$ {total:.2f}")

buf = io.BytesIO()
if total > 0:
    labels, values, colors, text_colors = [], [], [], []
    if valor_amplificador: labels.append("Amplificador"); values.append(valor_amplificador); colors.append('#e50914'); text_colors.append("white")
    if valor_driver: labels.append("Driver"); values.append(valor_driver); colors.append('#404040'); text_colors.append("white")
    if valor_controlador: labels.append("Controlador"); values.append(valor_controlador); colors.append('#bfbfbf'); text_colors.append("white")
    if valor_total_modulos: labels.append("Módulos Aux."); values.append(valor_total_modulos); colors.append('#ffffff'); text_colors.append("black")
    if valor_total_sinalizador: labels.append("Sinalizador Teto"); values.append(valor_total_sinalizador); colors.append('#00bfff'); text_colors.append("white")
    fig, ax = plt.subplots(figsize=(3.2, 3.2), facecolor='none')
    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, textprops={'fontsize': 9})
    for text in texts: text.set_color("white")
    for i, autotext in enumerate(autotexts): autotext.set_color(text_colors[i])
    for w in wedges: w.set_edgecolor("black"); w.set_linewidth(1.5)
    ax.axis('equal')
    plt.tight_layout()
    fig.patch.set_alpha(0)
    fig.savefig(buf, format="png", transparent=True, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    st.markdown(f'<img class="grafico-fixo" src="data:image/png;base64,{img_base64}">', unsafe_allow_html=True)
    
    # Lógica de botões
    if 'pdf_bytes' not in st.session_state:
        st.session_state.pdf_bytes = None
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("📄 Gerar Relatório"):
            st.session_state.pdf_bytes = gerar_pdf(
                amplificador, valor_amplificador, qtd_driver, valor_driver,
                controlador_tipo, valor_controlador, valor_total_modulos,
                sinalizador_tipo, valor_total_sinalizador, total, buf
            )
    with col2:
        if st.session_state.pdf_bytes:
            st.download_button(
                label="📥 Baixar PDF",
                data=st.session_state.pdf_bytes,
                file_name=f"relatorio_custos_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                mime='application/pdf',
                key="download_pdf_botao"
            )

# --- RODAPÉ E LOGO ---
st.markdown('<div class="rodape">© 2025 by Engesig. Created by Matteo Marques & Matheus Venzel</div>', unsafe_allow_html=True)

logo_path = Path("logo.png")
if logo_path.exists():
    logo_base64 = base64.b64encode(logo_path.read_bytes()).decode()
    st.markdown(f'<img class="logo-fixa" src="data:image/png;base64,{logo_base64}">', unsafe_allow_html=True)
