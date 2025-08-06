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
    /* Estilo corrigido para incluir as caixas de entrada de número */
    .stSelectbox div[data-baseweb="select"] *,
    .stSelectbox input, input[type="number"], 
    [data-testid="stNumberInput"] input {
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
    /* NOVO: Corrige o fundo branco do conteúdo do expander */
    [data-testid="stExpander"] {
        background-color: rgba(30, 30, 30, 0.7) !important;
    }
    </style>
