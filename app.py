import streamlit as st
import tempfile
import time
import pandas as pd
import io
import fitz  # PyMuPDF
from PIL import Image, ImageOps
from main import process_receipt_image, calculate_hash
from database import init_db, save_receipt, get_recent_receipts, get_all_receipts, get_receipt_by_hash
from reasoning.vector_store import index_receipt, query_receipts
from langchain_google_genai import ChatGoogleGenerativeAI
from config import api_key

# -----------------------------
# ⚙️ System Setup
# -----------------------------
try: init_db()
except: pass

st.set_page_config(page_title="BILLING PRO", page_icon="💳", layout="wide")

# -----------------------------
# 🎨 Professional Pro-SaaS Theme (Refined Obsidian)
# -----------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --bg-primary: #09090b;
        --bg-secondary: #18181b;
        --border-color: #27272a;
        --text-primary: #fafafa;
        --accent: #3b82f6;
    }

    .stApp { background-color: var(--bg-primary); color: var(--text-primary); font-family: 'Inter', sans-serif; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: var(--bg-primary) !important; border-right: 1px solid var(--border-color) !important; }
    
    /* Metrics */
    [data-testid="stMetric"] { background-color: var(--bg-secondary) !important; border: 1px solid var(--border-color) !important; padding: 1.5rem !important; border-radius: 12px !important; }
    
    /* Floating Assistant Bubble */
    .floating-assistant {
        position: fixed;
        bottom: 25px;
        right: 25px;
        z-index: 1000;
    }

    /* Professional Buttons */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease;
    }

    /* Hide UI Clutter */
    #MainMenu, footer, .stDeployButton { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------
# 🌐 State Management
# -----------------------------
if "receipt_data" not in st.session_state: st.session_state["receipt_data"] = None
if "current_image" not in st.session_state: st.session_state["current_image"] = None
if "chat_history" not in st.session_state: st.session_state["chat_history"] = []
if "show_assistant" not in st.session_state: st.session_state["show_assistant"] = False

# -----------------------------
# 🛠 Logic Helpers
# -----------------------------
def convert_pdf_to_image(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
    return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")

# -----------------------------
# ⬅️ Navigation & Records
# -----------------------------
with st.sidebar:
    st.markdown("### BILLING PRO")
    st.divider()
    st.markdown("#### HISTORY")
    try:
        recent = get_recent_receipts(limit=8)
        for r in recent:
            curr = r.currency or ""
            if st.button(f"{r.store_name or 'UNNAMED'} \n {curr}{r.total or 0}", key=f"h_{r.id}", use_container_width=True):
                st.session_state["receipt_data"] = r.raw_json
                st.rerun()
    except: pass

# -----------------------------
# 🏗 Main Dashboard Workspace
# -----------------------------
st.title("FINANCIAL INTELLIGENCE")

# Section 1: Command Bar
with st.container():
    files = st.file_uploader("UPLOAD DOCUMENTS", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True, label_visibility="collapsed")
    
    if files:
        b1, b2 = st.columns([1, 1])
        with b1:
            if st.button("EXECUTE ANALYSIS", type="primary", use_container_width=True):
                with st.status("ANALYZING..."):
                    for f in files:
                        img = convert_pdf_to_image(f.read()) if f.name.endswith(".pdf") else Image.open(f).convert("RGB")
                        st.session_state["current_image"] = img
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                            img.save(tmp.name, format="JPEG")
                            h = calculate_hash(tmp.name)
                            cached = get_receipt_by_hash(h)
                            if cached: st.session_state["receipt_data"] = cached.raw_json
                            else:
                                res_data, res_hash = process_receipt_image(tmp.name, use_cache=False)
                                save_receipt(res_data, image_hash=res_hash)
                                index_receipt(res_data, image_hash=res_hash)
                                st.session_state["receipt_data"] = res_data
                st.rerun()
        with b2:
            if st.button("VIEW ORIGINAL", use_container_width=True):
                if st.session_state["current_image"]:
                    st.image(st.session_state["current_image"], use_container_width=True)
                else:
                    st.warning("NO IMAGE LOADED")

st.divider()

# Section 2: Dashboard & Data Grid
data = st.session_state.get("receipt_data")
col_grid, col_stats = st.columns([1.2, 0.8])

with col_grid:
    if data:
        d = data if isinstance(data, dict) else data.model_dump()
        st.markdown("#### EXTRACTION SUMMARY")
        k1, k2, k3 = st.columns(3)
        k1.metric("MERCHANT", d['store_info']['name'] or "UNDEFINED")
        k2.metric("DATE", d['receipt_info']['date'] or "PENDING")
        curr = d.get('totals', {}).get('currency') or ""
        k3.metric("TOTAL", f"{curr}{d['totals']['total']}")
        
        st.markdown("#### LINE ITEMS")
        st.dataframe(pd.DataFrame(d['items']), use_container_width=True, hide_index=True)
    else:
        st.info("AWAITING INPUT FOR ANALYSIS")

with col_stats:
    st.markdown("#### ANALYTICS")
    all_recs = get_all_receipts()
    if all_recs:
        # Spending by Merchant Chart
        df_stats = pd.DataFrame([{"Merchant": r.store_name or "Unknown", "Total": r.total} for r in all_recs])
        merchant_spend = df_stats.groupby("Merchant")["Total"].sum().reset_index()
        st.bar_chart(merchant_spend.set_index("Merchant"))
        
        st.metric("TOTAL ASSETS PROCESSED", f"${sum(r.total for r in all_recs):,.2f}")
    else:
        st.caption("ANALYTICS WILL POPULATE AFTER DATA ENTRY")

# -----------------------------
# 💬 Persistent Floating Assistant (Bubble View)
# -----------------------------
st.markdown("""<div class='floating-assistant'>""", unsafe_allow_html=True)
with st.sidebar:
    st.divider()
    if st.button("💬 TOGGLE ASSISTANT", use_container_width=True):
        st.session_state["show_assistant"] = not st.session_state["show_assistant"]

if st.session_state["show_assistant"]:
    with st.container(border=True):
        st.markdown("#### AI FINANCIAL ADVISOR")
        chat_box = st.container(height=300)
        with chat_box:
            for msg in st.session_state["chat_history"]:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
        if prompt := st.chat_input("ASK ABOUT YOUR FINANCES"):
            st.session_state["chat_history"].append({"role": "user", "content": prompt})
            ctx = query_receipts(prompt)
            llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", api_key=api_key)
            resp = llm.invoke(f"HISTORY:\n{ctx}\n\nUSER: {prompt}")
            
            # Extract text if response is a list of blocks
            full_content = resp.content
            if isinstance(full_content, list):
                text_content = "".join([block['text'] for block in full_content if block.get('type') == 'text'])
            else:
                text_content = full_content
                
            st.session_state["chat_history"].append({"role": "assistant", "content": text_content})
            st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
