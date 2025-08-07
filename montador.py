import streamlit as st
from PIL import Image
import base64
from pathlib import Path
import matplotlib.pyplot as plt
import io
from fpdf import FPDF
import datetime
import tempfile
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


# --- FUNÇÃO DE PDF PARA TESTE ---
def gerar_pdf_teste():
    """Gera um PDF extremamente simples para verificar a integridade da biblioteca."""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=16)
        pdf.cell(0, 10, txt="Teste de PDF. Se voce consegue ler isso, o problema esta nos dados.", ln=True, align='C')
        return pdf.output()
    except Exception as e:
        # Se houver qualquer erro, ele será gravado no próprio PDF.
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=f"Ocorreu um erro ao gerar o PDF: {str(e)}")
        return pdf.output()


# --- INTERFACE PRINCIPAL (simplificada para o teste) ---
st.title("Teste de Geração de PDF")
st.warning("Esta é uma versão de teste. Apenas o botão de download abaixo está funcional.")

# --- BOTÃO DE DOWNLOAD DE TESTE ---
st.download_button(
    label="📄 Gerar e Baixar PDF de Teste",
    data=gerar_pdf_teste(),
    file_name="relatorio_teste.pdf",
    mime='application/pdf'
)

# --- RODAPÉ E LOGO ---
st.markdown('<div class="rodape">© 2025 by Engesig. Created by Matteo Marques & Matheus Venzel
