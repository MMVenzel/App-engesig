import streamlit as st
from PIL import Image
import base64
from pathlib import Path
import matplotlib.pyplot as plt
import io
from weasyprint import HTML  # <-- NOVA BIBLIOTECA DE PDF
import datetime
import os

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
    .grafico-fixo { width: 300px; z-index: 10000; background: none; position: fixed; top: 290px; left: 30px; }
    div[data-testid="stExpander"] summary { background-color: #1E1E1E !important; color: white !important; border-radius: 8px !important; padding: 0.5rem !important; }
    div[data-testid="stExpander"] summary svg { display: none; }
    div[data-testid="stExpander"] summary::after { content: ' ▼'; float: left; margin-right: 10px; transition: transform 0.2s ease-in-out; }
    div[data-testid="stExpander"][aria-expanded="true"] summary::after { transform: rotate(180deg); }
    div[data-testid="stExpander"] div[role="region"] { background-color: rgba(30, 30, 30, 0.7) !important; border-radius: 0 0 8px 8px !important; padding-top: 1rem !important; margin-top: -8px !important; }
    div[data-testid="stExpander"] div[role="region"] > div { background-color: transparent !important; }
    .rodape { position: fixed; bottom: 10px; left: 10px; color: #888; font-size: 12px; z-index: 9999; }
    .logo-fixa { position: fixed; top: 40px; left: 40px; width: 160px; z-index: 10000; }
    .subtotal-container { text-align: right; font-size: 1.1rem; font-weight: bold; color: #CCCCCC; margin-top: 10px; margin-bottom: 10px; }
    .subtotal-container span { color: white; font-size: 1.2rem; margin-left: 10px; }
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
    "Nano": {"3W": {"Single": 20.90, "Dual": 31.27, "Tri": 33.51}},
    "Micro": {"3W": {"Single": 14.89, "Dual": 19.09, "Tri": 20.56}, "OPT": {"Single": 13.97}, "Q-MAX": {"Single": 7.3}},
    "D-Max": {"3W": {"Single": 15.20, "Dual": 19.97, "Tri": 23.51}, "OPT": {"Single": 15.31}, "Q-MAX": {"Single": 9.1}},
    "Sinalizador": {"3W": {"Single": 14.89, "Dual": 19.09, "Tri": 20.56}, "OPT": {"Single": 17.09}, "Q-MAX": {"Single": 7.3}}
}
precos_cor_led = {
    "3W": {"Amber": 5.79, "Red": 3.58, "Blue": 3.58, "White": 3.58},
    "OPT": {"Amber": 1.36, "Red": 0.86, "Blue": 1.00, "White": 1.60},
    "Q-MAX": {"Amber": 1.36, "Red": 0.86, "Blue": 1.00, "White": 1.60}
}
limite_cores = {
    ("Nano", "3W"): 3, ("Micro", "3W"): 3, ("Micro", "OPT"): 1, ("Micro", "Q-MAX"): 1,
    ("D-Max", "3W"): 3, ("D-Max", "OPT"): 2, ("D-Max", "Q-MAX"): 1,
    ("Sinalizador", "3W"): 3, ("Sinalizador", "OPT"): 1, ("Sinalizador", "Q-MAX"): 1
}

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

# --- NOVA FUNÇÃO DE PDF USANDO WEASYPRINT (MUITO MAIS ROBUSTA) ---
def gerar_pdf(dados_relatorio):
    data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    img_bytes = dados_relatorio.get("imagem_bytes")
    
    # Converte a imagem em memória para um formato que o HTML entende (base64)
    imagem_html = ""
    if img_bytes and len(img_bytes) > 0:
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        imagem_html = f'<img src="data:image/png;base64,{img_b64}" style="width: 300px; display: block; margin: 20px auto;">'

    # Monta o relatório como uma página HTML
    html_string = f"""
    <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; font-size: 12px; }}
                h1 {{ text-align: center; color: #333; }}
                p {{ text-align: center; color: #666; font-size: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background-color: #f2f2f2; text-align: left; }}
                .total td {{ font-weight: bold; font-size: 14px; border-top: 2px solid black; }}
                .direita {{ text-align: right; }}
            </style>
        </head>
        <body>
            <h1>Relatório de Custo - Sinalização</h1>
            <p>Data de Geração: {data}</p>
            
            <h2>Resumo dos Componentes</h2>
            <table>
                <tr>
                    <th>Item</th>
                    <th class="direita">Valor</th>
                </tr>
                <tr>
                    <td>Subtotal Sirene e Controlador</td>
                    <td class="direita">R$ {dados_relatorio['subtotal_eletronicos']:.2f}</td>
                </tr>
                """
    if dados_relatorio['valor_total_modulos'] > 0:
        html_string += f"""
                <tr>
                    <td>Subtotal Módulos Auxiliares</td>
                    <td class="direita">R$ {dados_relatorio['valor_total_modulos']:.2f}</td>
                </tr>"""
    if dados_relatorio['valor_total_sinalizador'] > 0:
        html_string += f"""
                <tr>
                    <td>Subtotal Sinalizador ({dados_relatorio['sinalizador_tipo']})</td>
                    <td class="direita">R$ {dados_relatorio['valor_total_sinalizador']:.2f}</td>
                </tr>"""
    
    html_string += f"""
                <tr class="total">
                    <td>CUSTO TOTAL:</td>
                    <td class="direita">R$ {dados_relatorio['total']:.2f}</td>
                </tr>
            </table>
            
            {imagem_html}
        </body>
    </html>
    """
    
    # Converte o HTML para PDF e retorna os bytes
    return HTML(string=html_string).write_pdf()


# --- INTERFACE PRINCIPAL ---
st.title("Central de Custos | Sinalização")

st.markdown("### 🔊 Sirene e Controlador")
amplificador = st.selectbox("Escolha o amplificador:", list(precos_amplificador.keys()))
qtd_driver = 0
if amplificador in ["100W", "200W"]:
    if st.selectbox("Acompanha driver?", ["Não", "Sim"]) == "Sim":
        qtd_driver = 1 if amplificador == "100W" else 2
controlador_tipo = st.selectbox("Escolha o tipo de controlador:", list(precos_controlador.keys()))

subtotal_eletronicos = precos_amplificador[amplificador] + (qtd_driver * preco_driver) + precos_controlador[controlador_tipo]
st.markdown(f'<p class="subtotal-container">Subtotal de Sirene e Controlador: <span>R$ {subtotal_eletronicos:.2f}</span></p>', unsafe_allow_html=True)
st.markdown("---")

st.markdown("### 🔧 Módulos Auxiliares")
qtd_modelos_modulos = st.number_input("Quantos modelos de módulos deseja adicionar?", min_value=0, step=1, value=0)
valores_modulos = []
for i in range(qtd_modelos_modulos):
    with st.expander(f"Modelo de Módulo Auxiliar #{i+1}"):
        tipo_modulo = st.selectbox(f"Tipo de módulo:", ["Nano", "Micro", "D-Max"], key=f"tipo_modulo_{i}")
        qtd_mod = st.number_input(f"Quantidade de módulos:", min_value=1, step=1, value=1, key=f"qtd_modulo_{i}")
        tipos_led_disponiveis = list(precos_tipo_led_config[tipo_modulo].keys())
        tipo_led = st.selectbox(f"Tipo de LED:", tipos_led_disponiveis, key=f"tipo_led_{i}")
        max_cores = limite_cores.get((tipo_modulo, tipo_led), 1)
        cols = st.columns(4)
        usar_amber = cols[0].checkbox("Amber", key=f"amber_{i}")
        usar_red = cols[1].checkbox("Red", key=f"red_{i}")
        usar_blue = cols[2].checkbox("Blue", key=f"blue_{i}")
        usar_white = cols[3].checkbox("White", key=f"white_{i}")
        cores_escolhidas = [c for c, u in zip(["Amber", "Red", "Blue", "White"], [usar_amber, usar_red, usar_blue, usar_white]) if u]
        if len(cores_escolhidas) > max_cores:
            st.error(f"⚠️ Máximo de {max_cores} cor(es) para esta configuração.")
            continue
        qtd_leds_por_cor = {}
        for cor in cores_escolhidas:
            limite = calcular_limite_leds(tipo_modulo, tipo_led, cores_escolhidas)
            qtd = st.number_input(f"Qtd LEDs {cor} (máx {limite}):", min_value=0, max_value=limite, step=1, key=f"qtd_{cor}_{i}")
            qtd_leds_por_cor[cor] = qtd
        config_led = "Single"
        if len(cores_escolhidas) > 0: config_led = ["Single", "Dual", "Tri"][len(cores_escolhidas) - 1]
        preco_placa = precos_tipo_led_config[tipo_modulo][tipo_led].get(config_led, 0)
        preco_base_mod = precos_modulo.get(tipo_modulo, 0)
        preco_leds = sum(qtd * precos_cor_led[tipo_led][cor] for cor, qtd in qtd_leds_por_cor.items())
        valores_modulos.append((preco_base_mod + preco_placa + preco_leds) * qtd_mod)

valor_total_modulos = sum(valores_modulos)
if qtd_modelos_modulos > 0:
    st.markdown(f'<p class="subtotal-container">Subtotal dos Módulos Auxiliares: <span>R$ {valor_total_modulos:.2f}</span></p>', unsafe_allow_html=True)
st.markdown("---")

st.markdown("### 🚨 Sinalizador de Teto")
sinalizador_tipo = st.selectbox("Escolha o sinalizador de teto:", list(precos_sinalizador_teto.keys()))

valor_total_sinalizador = 0
if sinalizador_tipo != "Nenhum":
    base_sinalizador = precos_sinalizador_teto.get(sinalizador_tipo, 0)
    tipo_led_sinalizador = st.selectbox("Tipo de LED do Sinalizador:", ["3W", "OPT", "Q-MAX"], key="sinalizador_led_type")
    qtd_modelos_sinalizador = st.number_input("Quantos modelos de módulos para o sinalizador?", min_value=0, step=1, value=0)
    modulos_sinalizador = 0
    total_modulos_sinalizador_count = 0
    for j in range(qtd_modelos_sinalizador):
        with st.expander(f"Modelo de Módulo Sinalizador #{j+1}"):
            qtd_mod_sinalizador = st.number_input(f"Qtd de módulos do modelo:", min_value=1, step=1, value=1, key=f"qtd_mod_sinalizador_{j}")
            total_modulos_sinalizador_count += qtd_mod_sinalizador
            max_cores = limite_cores.get(("Sinalizador", tipo_led_sinalizador), 1)
            cols_s = st.columns(4)
            usar_amber_s = cols_s[0].checkbox("Amber", key=f"amber_s_{j}")
            usar_red_s = cols_s[1].checkbox("Red", key=f"red_s_{j}")
            usar_blue_s = cols_s[2].checkbox("Blue", key=f"blue_s_{j}")
            usar_white_s = cols_s[3].checkbox("White", key=f"white_s_{j}")
            cores_s = [c for c, u in zip(["Amber", "Red", "Blue", "White"], [usar_amber_s, usar_red_s, usar_blue_s, usar_white_s]) if u]
            if len(cores_s) > max_cores:
                st.error(f"⚠️ Máximo de {max_cores} cor(es) para esta configuração.")
                continue
            leds_s = {}
            total_leds_no_modulo = 0
            for cor_s in cores_s:
                limite_s = calcular_limite_leds("Sinalizador", tipo_led_sinalizador, cores_s)
                qtd_s = st.number_input(f"Qtd LEDs {cor_s} (máx {limite_s}):", min_value=0, max_value=limite_s, step=1, key=f"qtd_s_{cor_s}_{j}")
                leds_s[cor_s] = qtd_s
                total_leds_no_modulo += qtd_s
            config_led_s = "Single"
            if len(cores_s) > 0: config_led_s = ["Single", "Dual", "Tri"][len(cores_s) - 1]
            if tipo_led_sinalizador == "OPT":
                preco_placa_s = precos_tipo_led_config["Sinalizador"][tipo_led_sinalizador].get(config_led_s, 0)
            else:
                preco_placa_s = precos_tipo_led_config["D-Max"][tipo_led_sinalizador].get(config_led_s, 0)
            preco_leds_s = sum(qtd * precos_cor_led[tipo_led_sinalizador][cor] for cor, qtd in leds_s.items())
            valor_por_modelo_s = preco_placa_s + preco_leds_s
            if sinalizador_tipo == "Sirius" and total_leds_no_modulo >= 6:
                valor_por_modelo_s += 10.80
            modulos_sinalizador += valor_por_modelo_s * qtd_mod_sinalizador
    custo_kit = precos_kit_sinalizador.get(sinalizador_tipo, 0) * total_modulos_sinalizador_count
    valor_total_sinalizador = base_sinalizador + modulos_sinalizador + custo_kit

if sinalizador_tipo != "Nenhum":
    st.markdown(f'<p class="subtotal-container">Subtotal do Sinalizador de Teto: <span>R$ {valor_total_sinalizador:.2f}</span></p>', unsafe_allow_html=True)
st.markdown("---")

# --- CÁLCULO FINAL E BOTÃO ---
total = subtotal_eletronicos + valor_total_modulos + valor_total_sinalizador
st.subheader(f"💵 Custo Estimado Total: R$ {total:.2f}")

if total > 0:
    buf = io.BytesIO()
    labels, values, colors, text_colors = [], [], [], []
    if subtotal_eletronicos > 0: labels.append("Sirene/Controlador"); values.append(subtotal_eletronicos); colors.append('#e50914'); text_colors.append("white")
    if valor_total_modulos > 0: labels.append("Módulos Aux."); values.append(valor_total_modulos); colors.append('#ffffff'); text_colors.append("black")
    if valor_total_sinalizador > 0: labels.append("Sinalizador Teto"); values.append(valor_total_sinalizador); colors.append('#00bfff'); text_colors.append("white")
    if values:
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

    dados_para_pdf = {
        "subtotal_eletronicos": subtotal_eletronicos,
        "valor_total_modulos": valor_total_modulos,
        "sinalizador_tipo": sinalizador_tipo,
        "valor_total_sinalizador": valor_total_sinalizador,
        "total": total,
        "imagem_bytes": buf.getvalue()
    }
    
    st.download_button(
        label="📄 Gerar e Baixar Relatório",
        data=gerar_pdf(dados_para_pdf),
        file_name=f"relatorio_custos_{datetime.now().strftime('%Y%m%d-%H%M')}.pdf",
        mime='application/pdf'
    )

# --- RODAPÉ E LOGO ---
st.markdown('<div class="rodape">© 2025 by Engesig. Created by Matteo Marques & Matheus Venzel</div>', unsafe_allow_html=True)
logo_path = Path("logo.png")
if logo_path.exists():
    logo_base64 = base64.b64encode(logo_path.read_bytes()).decode()
    st.markdown(f'<img class="logo-fixa" src="data:image/png;base64,{logo_base64}">', unsafe_allow_html=True)
