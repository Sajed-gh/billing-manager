import streamlit as st
import tempfile
import time
import pandas as pd
import io
import fitz  # PyMuPDF
from PIL import Image, ImageOps
from main import process_receipt_image, calculate_hash
from database import init_db, save_receipt, get_recent_receipts, get_all_receipts, get_receipt_by_hash, delete_receipt
from reasoning.vector_store import index_receipt, query_receipts
import google.generativeai as genai
from config import api_key
from user_auth.auth import authenticate_user, create_user

# -----------------------------
# ⚙️ System Setup
# -----------------------------
try: init_db()
except: pass

st.set_page_config(page_title="BILLING PRO", page_icon="💳", layout="wide")

# -----------------------------
# 🎨 Professional Pro-SaaS Theme (Zinc & Obsidian)
# -----------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --bg-primary: #09090b;
        --bg-secondary: #18181b;
        --border-color: #27272a;
        --text-primary: #fafafa;
        --text-muted: #a1a1aa;
        --accent: #3b82f6;
    }

    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: var(--bg-primary) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    
    h1, h2, h3, h4 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
    }

    [data-testid="stMetric"] {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
    }

    .stButton>button {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        width: 100%;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        border-color: var(--accent) !important;
    }

    #MainMenu, footer, .stDeployButton { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------
# 🌐 Session & Auth Management
# -----------------------------
if "user" not in st.session_state: st.session_state["user"] = None
if "receipt_data" not in st.session_state: st.session_state["receipt_data"] = None
if "current_receipt_id" not in st.session_state: st.session_state["current_receipt_id"] = None
if "current_image" not in st.session_state: st.session_state["current_image"] = None
if "chat_history" not in st.session_state: st.session_state["chat_history"] = []
if "show_assistant" not in st.session_state: st.session_state["show_assistant"] = False
if "is_processing" not in st.session_state: st.session_state["is_processing"] = False

def login_screen():
    st.title("BILLING PRO")
    tab1, tab2 = st.tabs(["LOGIN", "CREATE ACCOUNT"])
    
    with tab1:
        with st.form("login_form"):
            u = st.text_input("USERNAME")
            p = st.text_input("PASSWORD", type="password")
            submitted = st.form_submit_button("SIGN IN")
            if submitted:
                user = authenticate_user(u, p)
                if user:
                    st.session_state["user"] = user
                    st.rerun()
                else:
                    st.error("INVALID CREDENTIALS")
                
    with tab2:
        with st.form("register_form"):
            nu = st.text_input("NEW USERNAME")
            np = st.text_input("NEW PASSWORD", type="password")
            submitted = st.form_submit_button("REGISTER")
            if submitted:
                if create_user(nu, np):
                    st.success("ACCOUNT CREATED. PLEASE LOGIN.")
                else:
                    st.error("USERNAME ALREADY EXISTS OR INVALID INPUT")

if st.session_state["user"] is None:
    login_screen()
    st.stop()

# -----------------------------
# 🛠 Logic Helpers
# -----------------------------
user = st.session_state["user"]

def convert_pdf_to_image(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
    return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")

# -----------------------------
# ⬅️ Navigation & Records
# -----------------------------
with st.sidebar:
    st.markdown(f"### WELCOME, {user['username'].upper()}")
    if st.button("LOGOUT"):
        st.session_state["user"] = None
        st.rerun()
        
    st.divider()
    st.markdown("#### HISTORY")
    try:
        recent = get_recent_receipts(user["id"], limit=8)
        for r in recent:
            curr = r.currency or ""
            if st.button(f"{r.store_name or 'UNNAMED'} \n {curr}{r.total or 0}", key=f"h_{r.id}", use_container_width=True):
                st.session_state["receipt_data"] = r.raw_json
                st.session_state["current_receipt_id"] = r.id
                st.rerun()
    except: pass

# -----------------------------
# 🏗 Main Dashboard Workspace
# -----------------------------
st.title("FINANCIAL INTELLIGENCE")

with st.container():
    files = st.file_uploader("UPLOAD DOCUMENTS", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True, label_visibility="collapsed")
    
    if files:
        if st.button("EXECUTE ANALYSIS", type="primary", use_container_width=True):
            st.session_state["is_processing"] = True
            with st.status("ANALYZING DATA..."):
                for f in files:
                    img = convert_pdf_to_image(f.getvalue()) if f.name.endswith(".pdf") else Image.open(io.BytesIO(f.getvalue())).convert("RGB")
                    st.session_state["current_image"] = img
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                        img.save(tmp.name, format="JPEG")
                        h = calculate_hash(tmp.name)
                        cached = get_receipt_by_hash(h, user["id"])
                        if cached: 
                            st.session_state["receipt_data"] = cached.raw_json
                            st.session_state["current_receipt_id"] = cached.id
                        else:
                            res_data, res_hash = process_receipt_image(tmp.name, use_cache=False)
                            new_r = save_receipt(res_data, user["id"], image_hash=res_hash)
                            index_receipt(res_data, image_hash=res_hash)
                            st.session_state["receipt_data"] = res_data
                            st.session_state["current_receipt_id"] = new_r.id
            st.session_state["is_processing"] = False
            st.rerun()

st.divider()

if not st.session_state["is_processing"]:
    data = st.session_state.get("receipt_data")
    col_grid, col_stats = st.columns([1.2, 0.8])

    with col_grid:
        if data:
            d = data if isinstance(data, dict) else data.model_dump()
            st.markdown("#### EXTRACTION SUMMARY")
            k1, k2, k3 = st.columns(3)
            k1.metric("MERCHANT", d.get('store_info', {}).get('name') or "UNDEFINED")
            k2.metric("DATE", d.get('receipt_info', {}).get('date') or "PENDING")
            curr = d.get('totals', {}).get('currency') or ""
            k3.metric("TOTAL", f"{curr}{d.get('totals', {}).get('total') or 0.0}")
            
            st.markdown("#### LINE ITEMS")
            st.dataframe(pd.DataFrame(d.get('items', [])), use_container_width=True, hide_index=True)

            st.divider()
            if st.button("🗑️ DELETE RECORD", type="secondary", use_container_width=True):
                if st.session_state.get("current_receipt_id"):
                    if delete_receipt(st.session_state["current_receipt_id"], user["id"]):
                        st.success("RECORD DELETED")
                        st.session_state["receipt_data"] = None
                        st.session_state["current_receipt_id"] = None
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("FAILED TO DELETE RECORD")
        else:
            st.info("AWAITING INPUT")

    with col_stats:
        if data:
            st.markdown("#### ANALYTICS")
            all_recs = get_all_receipts(user["id"])
            if all_recs:
                # Dashboard Selection Dropdown
                view_option = st.selectbox(
                    "SELECT PERSPECTIVE",
                    ["SUMMARY", "SPENDING TREND", "MERCHANT ALLOCATION", "TOP ITEMS"],
                    label_visibility="collapsed"
                )
                
                # Convert to DataFrame for easier analysis
                df_stats = pd.DataFrame([
                    {
                        "Merchant": r.store_name or "Unknown",
                        "Total": r.total or 0.0,
                        "Date": pd.to_datetime(r.date, dayfirst=True, errors='coerce'),
                        "Currency": r.currency or "N/A",
                        "Items": r.num_items or 0
                    } for r in all_recs
                ])
                
                st.divider()

                if view_option == "SUMMARY":
                    # ... (rest of summary code)
                    st.markdown("#### VOLUME SUMMARY")
                    m1, m2 = st.columns(2)
                    m1.metric("TOTAL RECORDS", len(all_recs))
                    total_items = df_stats["Items"].sum()
                    m2.metric("TOTAL ITEMS PROCESSED", int(total_items))
                    st.caption(f"ANALYTICS BASED ON {len(all_recs)} ANALYZED DOCUMENTS")
                    
                    # Export options
                    st.divider()
                    st.markdown("#### EXPORT DATA")
                    c1, c2 = st.columns(2)
                    csv = df_stats.to_csv(index=False).encode('utf-8')
                    c1.download_button("DOWNLOAD CSV", data=csv, file_name="receipts.csv", mime="text/csv", use_container_width=True)
                    
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df_stats.to_excel(writer, index=False, sheet_name='Receipts')
                    c2.download_button("DOWNLOAD EXCEL", data=output.getvalue(), file_name="receipts.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

                elif view_option == "SPENDING TREND":
                    # 2. Spending Trend (Over Time)
                    st.markdown("#### TRANSACTION VOLUME")
                    if not df_stats["Date"].isna().all():
                        trend_df = df_stats.dropna(subset=["Date"]).sort_values("Date")
                        trend_df = trend_df.groupby("Date").size().reset_index(name='Count')
                        st.line_chart(trend_df.set_index("Date"))
                    else:
                        st.info("NO VALID DATE DATA FOUND")

                elif view_option == "MERCHANT ALLOCATION":
                    # 3. Merchant Distribution
                    st.markdown("#### MERCHANT FREQUENCY")
                    merchant_dist = df_stats.groupby("Merchant").size().sort_values(ascending=False)
                    st.bar_chart(merchant_dist)

                elif view_option == "TOP ITEMS":
                    # 4. Item Analytics
                    st.markdown("#### TOP ITEMS")
                    all_items = []
                    for r in all_recs:
                        for item in r.items:
                            all_items.append({
                                "Item": item.name,
                                "Cost": item.total_price or 0.0
                            })
                    if all_items:
                        df_items_all = pd.DataFrame(all_items)
                        top_items = df_items_all.groupby("Item")["Cost"].sum().sort_values(ascending=False).head(10)
                        st.table(top_items)
                    
            else:
                st.caption("NO DATA AVAILABLE FOR ANALYSIS")
        else:
            st.empty()
else:
    st.info("PROCESSING DATA... PLEASE WAIT.")

# Assistant
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

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content(f"HISTORY:\n{ctx}\n\nUSER: {prompt}")

            text_content = resp.text

            st.session_state["chat_history"].append({"role": "assistant", "content": text_content})
            st.rerun()

