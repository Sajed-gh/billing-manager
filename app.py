import streamlit as st
import tempfile
import time
from PIL import Image, ImageOps
from main import process_receipt_image

st.set_page_config(page_title="Invoice Parser Demo", page_icon="🧾", layout="wide")

st.title("Invoice Parser Proof of Concept")
st.markdown(
    """
    Upload a scanned receipt and get structured data.
    """
)

# Initialize session state
if "receipt_data" not in st.session_state:
    st.session_state["receipt_data"] = None
if "view_choice" not in st.session_state:
    st.session_state["view_choice"] = "Invoice"

# File uploader
uploaded_file = st.file_uploader("Upload receipt image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Save temp image
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    temp_file.write(uploaded_file.read())
    image_path = temp_file.name

    # Display the image (resized & correctly oriented)
    image = Image.open(image_path)
    image = ImageOps.exif_transpose(image)
    max_width = 400
    ratio = max_width / image.width
    resized_image = image.resize((max_width, int(image.height * ratio)))

    col_image, col_output = st.columns([1, 1])
    with col_image:
        st.image(resized_image, caption="Receipt", use_container_width=False)

    # Process the receipt only if not done yet
    if st.session_state["receipt_data"] is None:
        with col_output:
            status_text = st.empty()  # placeholder for spinner text
            status_text.text("🔍 Extracting data... Please wait")
            start_time = time.time()
            try:
                receipt_obj = process_receipt_image(image_path)
                st.session_state["receipt_data"] = receipt_obj
                elapsed = time.time() - start_time
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()
            # Update the placeholder text
            status_text.text(f"✅ Extraction complete in {elapsed:.1f} sec")
    else:
        receipt_obj = st.session_state["receipt_data"]

    # --- View buttons ---
    with col_output:
        st.markdown("**View as:**")
        btn_json, btn_invoice = st.columns([1, 1])
        if btn_json.button("JSON"):
            st.session_state["view_choice"] = "JSON"
        if btn_invoice.button("Invoice"):
            st.session_state["view_choice"] = "Invoice"

        # Display the selected view
        if st.session_state["view_choice"] == "JSON":
            st.subheader("JSON Output")
            st.json(receipt_obj.model_dump(), expanded=False)
        else:
            st.subheader("Invoice View")
            store = receipt_obj.store_info
            totals = receipt_obj.totals
            items = receipt_obj.items
            receipt_info = receipt_obj.receipt_info

            # Header info
            st.markdown(f"""
            **{store.name}**  
            {store.address or ''}  
            {store.phone or ''}  
            **Date:** {receipt_info.date or ''}  
            **Time:** {receipt_info.time or ''}  
            ---
            """)

            # Items table
            st.table(
                [{"Qty": item.quantity or "", "Item": item.name,
                  "Unit": item.unit_price or "", "Total": item.total_price or ""} for item in items]
            )

            # Totals section
            st.markdown(f"""
            **Total:** {totals.total or 0}  
            **Paid:** {totals.paid or 0}  
            **Change:** {totals.change or 0}  
            **Items:** {totals.num_items or len(items)}
            ---
            """)
