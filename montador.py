import streamlit as st
from PIL import Image
import base64
from pathlib import Path
import matplotlib.pyplot as plt
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from datetime import datetime

# --- CONFIGURAÇÃO INICIAL DA PÁGINA ---
st.set_page_config(
    page_title="Engesig | Central de Custos",
    page_icon="logo_engesig.ico",
    layout="centered"
)

# --- ESTILO VISUAL (CSS) ---
CSS_STYLE = """
<style>
    :root { color-scheme: dark; }
    .stApp { background-color: black !important; color: white !important; }
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; font-size: 16px; color: white; }
    h1, h2, h3, h4, h5, h6, p, label, div, span { color: white !important; }
    .stSelectbox div[data-baseweb="select"] *, .stSelectbox input, input[type="number"], [data-testid="stNumberInput"] input { color: white !important; background-color: rgba(30, 30, 30, 0.7) !important; }
    div[data-baseweb="popover"] * { color: white !important; background-color: #333 !important; }
    header, [data-testid="stHeader"] { visibility: hidden; height: 0rem; padding: 0rem; }
    input:focus, select:focus, textarea:focus, .stSelectbox:focus-within { animation: pulse 0.6s; }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 0, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }
    }
    button { background-color: #222 !important; color: white !important; border: 1px solid #444 !important; border-radius: 8px !important; padding: 0.5em 1em !important; transition: 0.3s ease; }
    button:hover { background-color: #333 !important; border: 1px solid white !important; color: white !important; }
    button svg { fill: white !important; }
    .grafico-fixo { width: 300px; height: 300px; z-index: 10000; background: none; position: fixed; top: 290px; left: 30px; }
    div[data-testid="stExpander"] summary { background-color: #1E1E1E !important; color: white !important; border-radius: 8px !important; padding: 0.5rem !important; }
    div[data-testid="stExpander"] summary svg { display: none; }
    div[data-testid="stExpander"] summary::after { content: ' ▼'; float: left; margin-right: 10px; transition: transform 0.2s ease-in-out; }
    div[data-testid="stExpander"][aria-expanded="true"] summary::after { transform: rotate(180deg); }
    div[data-testid="stExpander"] div[role="region"] { background-color: rgba(30, 30, 30, 0.7) !important; border-radius: 0 0 8px 8px !important; padding-top: 1rem !important; margin-top: -8px !important; }
    div[data-testid="stExpander"] div[role="region"] > div { background-color: transparent !important; }
    .rodape { position: fixed; bottom: 10px; left: 10px; color: #888; font-size: 12px; z-index: 9999; }
    .logo-fixa { position: fixed; top: 40px; left: 40px; width: 160px; z-index: 10000; }
    .subtotal-container { text-align: right; font-size: 1.2rem; font-weight: bold; color: #CCCCCC; margin-top: 10px; margin-bottom: 10px; }
    .subtotal-container span { color: white; font-size: 1.4rem; margin-left: 10px; }
    .observacao { font-size: 0.8rem; color: #888; text-align: right; margin-top: -8px; }

    /* ALTERADO: Esconde o gráfico E A LOGO em telas pequenas (celulares) */
    @media (max-width: 768px) {
        .grafico-fixo, .logo-fixa {
            display: none !important;
        }
    }
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)

# --- DADOS E PREÇOS ---
precos_amplificador = {"Nenhum": 0, "100W": 338.19, "200W": 547.47, "Moto": 392.55}
preco_driver = 319.81
precos_controlador = {
    "Nenhum": 0, "Micro 3B Moto": 102.98, "Micro 3B C/ Mic": 145.50, "Micro 4B com Mic": 145.36,
    "Handheld 9B Magnético": 236.44, "Controlador Fixo 15B": 206.30, "Controlador Fixo 17B": 216.60
}
precos_modulo = {"Nenhum": 0, "Nano": 39.67, "Micro": 25.69, "D-Max": 28.17}
precos_sinalizador_teto = {"Nenhum": 0, "Sirius": 634.17, "Brutale": 717.07}
precos_kit_sinalizador = {"Sirius": 3.00, "Brutale": 7.00}
precos_tipo_led_config = {
    "Nano": {"3W": {"Single": 20.90, "Dual": 31.27, "Tri": 33.51}}}
precos_cor_led = {
    "3W": {"Amber": 5.79, "Red": 3.58, "Blue": 3.58, "White": 3.58}
}

limite_cores = {("Nano", "3W"): 3}

# --- FUNÇÕES AUXILIARES ---
def calcular_limite_leds(tipo_modulo, tipo_led, cores_escolhidas):
    num_cores = len(cores_escolhidas)
    if tipo_modulo == "Micro":
        if tipo_led == "3W":
            if num_cores == 1: return 9
            elif num_cores == 2: return 4
            elif num_cores == 3: return 3
        return 3
    elif tipo_modulo == "D-Max":
        if tipo_led == "3W": return 18 if num_cores == 1 else 6
        elif tipo_led == "OPT": return 12 if num_cores == 1 else 6
        elif tipo_led == "Q-MAX": return 4
    elif tipo_modulo == "Nano" and tipo_led == "3W": return 9 if num_cores == 1 else 3
    elif tipo_modulo == "Sinalizador":
        if tipo_led == "3W":
            if num_cores == 1: return 9
            elif num_cores == 2: return 6
            elif num_cores == 3: return 3
        elif tipo_led == "OPT": return 4
        return 3
    return 18

def gerar_pdf(dados_relatorio):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2.0, height - 50, "Relatório de Custo - Sinalização")
    p.setFont("Helvetica", 10)
    data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    p.drawCentredString(width / 2.0, height - 70, f"Data de Geração: {data}")

    y = height - 120
    p.setFont("Helvetica-Bold", 12)
    p.drawString(72, y, "Resumo dos Componentes")
    p.line(72, y - 5, width - 72, y - 5)
    y -= 25

    p.setFont("Helvetica", 11)
    p.drawString(72, y, "Subtotal Maxfinder:")
    p.drawRightString(width - 72, y, f"R$ {dados_relatorio['subtotal_eletronicos']:.2f}")
    y -= 20
    
    if dados_relatorio['valor_total_modulos'] > 0:
        p.drawString(72, y, "Subtotal Módulos Auxiliares:")
        p.drawRightString(width - 72, y, f"R$ {dados_relatorio['valor_total_modulos']:.2f}")
        y -= 20
        
    if dados_relatorio['valor_total_sinalizador'] > 0:
        p.drawString(72, y, f"Subtotal Sinalizador ({dados_relatorio['sinalizador_tipo']}):")
        p.drawRightString(width - 72, y, f"R$ {dados_relatorio['valor_total_sinalizador']:.2f}")
        y -= 20

    y -= 10
    p.line(72, y, width - 72, y)
    y -= 18
    p.setFont("Helvetica-Bold", 14)
    p.drawString(72, y, "CUSTO TOTAL:")
    p.drawRightString(width - 72, y, f"R$ {dados_relatorio['total']:.2f}")

    img_bytes = dados_relatorio.get("imagem_bytes")
    if img_bytes and len(img_bytes) > 0:
        try:
            pil_image = Image.open(io.BytesIO(img_bytes))
            p.drawImage(ImageReader(pil_image), x=(width - 300) / 2.0, y=y-250, width=300, height=300, preserveAspectRatio=True, mask='auto')
        except Exception:
            p.drawString(72, y-30, "Erro ao processar imagem do gráfico.")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.getvalue()

# --- INTERFACE PRINCIPAL ---
st.title("Central de Custos | Sinalização")

st.markdown("### 🔊 Maxfinder")
amplificador = st.selectbox("Escolha o amplificador:", list(precos_amplificador.keys()))
qtd_driver = 0
if amplificador in ["100W", "200W"]:
    if st.selectbox("Acompanha driver?", ["Não", "Sim"]) == "Sim":
        qtd_driver = 1 if amplificador == "100W" else 2

# --- Adicionando a checkbox "Adicionar suporte de driver" --- 
suporte_driver = st.checkbox("Adicionar suporte de driver (R$ 50,00 por driver)")

# Calcular o custo adicional se a checkbox for marcada
custo_suporte_driver = 0
if suporte_driver:
    custo_suporte_driver = 50 * qtd_driver  # Adiciona R$ 50,00 por cada driver (1 ou 2)
    
# Subtotal de eletrônicos incluindo o custo do suporte de driver
subtotal_eletronicos = precos_amplificador[amplificador] + (qtd_driver * preco_driver) + precos_controlador["Micro 3B Moto"] + custo_suporte_driver
st.markdown(f'<p class="subtotal-container">Subtotal Maxfinder (incluindo suporte de driver): <span>R$ {subtotal_eletronicos:.2f}</span></p>', unsafe_allow_html=True)
st.markdown("---")
