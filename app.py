import streamlit as st
import tempfile
import time
from PIL import Image, ImageOps
from main import process_receipt_image
from ocr import extract_text, draw_bpolys
import traceback

# -----------------------------
# 🧾 Streamlit App Configuration
# -----------------------------
st.set_page_config(page_title="Invoice Parsing Agent – Proof of Concept", page_icon="🧾", layout="wide")
st.title("🧾 Invoice Understanding Agent – Proof of Concept")
st.caption("Upload a scanned receipt to extract structured data automatically.")

# -----------------------------
# 🌐 Session State Initialization
# -----------------------------
if "receipt_data" not in st.session_state:
    st.session_state["receipt_data"] = None
if "last_uploaded_name" not in st.session_state:
    st.session_state["last_uploaded_name"] = None
if "status_message" not in st.session_state:
    st.session_state["status_message"] = ""
if "ocr_bpolys" not in st.session_state:
    st.session_state["ocr_bpolys"] = None
if "view_mode" not in st.session_state:
    st.session_state["view_mode"] = "Invoice"

# -----------------------------
# 📤 File Uploader
# -----------------------------
uploaded_file = st.file_uploader("Upload a receipt image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Reset session state if new file uploaded
    if uploaded_file.name != st.session_state["last_uploaded_name"]:
        st.session_state.update({
            "receipt_data": None,
            "ocr_bpolys": None,
            "last_uploaded_name": uploaded_file.name,
            "status_message": "",
        })

    # Save temp image
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    temp_file.write(uploaded_file.read())
    image_path = temp_file.name

    # Proper orientation & convert to RGB
    image = Image.open(image_path).convert("RGB")
    image = ImageOps.exif_transpose(image)
    max_width = 400
    ratio = max_width / image.width
    resized_image = image.resize((max_width, int(image.height * ratio)))

    # Layout: Image (left) + Output (right)
    col_image, col_output = st.columns([1, 1])

    # -----------------------------
    # 📸 Left Column: Image / OCR
    # -----------------------------
    with col_image:
        st.markdown("### 📸 Image View")

        img_choice = st.segmented_control(
            "Image View",
            ["Original", "OCR Boxes"],
            key="image_view",
            label_visibility="collapsed",
            default="Original",
        )

        if img_choice == "OCR Boxes" and st.session_state["ocr_bpolys"]:
            ocr_img = ImageOps.exif_transpose(st.session_state["ocr_bpolys"])
            ratio = max_width / ocr_img.width
            resized_ocr = ocr_img.resize((max_width, int(ocr_img.height * ratio)))
            st.image(resized_ocr, caption="OCR Bounding Boxes", width="content")
        else:
            st.image(resized_image, caption="Uploaded Receipt", width="content")

    # -----------------------------
    # 🧠 Right Column: Pipeline & Output
    # -----------------------------
    with col_output:
        receipt_obj = st.session_state.get("receipt_data")

        if receipt_obj is None:
            status_placeholder = st.empty()
            status_placeholder.text("🔍 Extracting data... Please wait")

            start_time = time.time()
            try:
                receipt_obj = process_receipt_image(image_path)
                st.session_state["receipt_data"] = receipt_obj
                elapsed = time.time() - start_time
                st.session_state["status_message"] = f"✅ Extraction complete in {elapsed:.1f} sec"

                # OCR visualization
                extracted_text = extract_text(image_path)
                st.session_state["ocr_bpolys"] = draw_bpolys(image_path, extracted_text)

                status_placeholder.text(st.session_state["status_message"])

            except Exception as e:
                st.session_state["status_message"] = f"❌ Error: {e}"
                status_placeholder.text(st.session_state["status_message"])
                st.error("An error occurred while processing the image. See traceback below:")
                st.text(traceback.format_exc())
                receipt_obj = None

        st.info(st.session_state["status_message"])

        # View mode buttons
        view_cols = st.columns([1, 1])
        with view_cols[0]:
            if st.button("🧾 Invoice View", use_container_width=True):
                st.session_state["view_mode"] = "Invoice"
        with view_cols[1]:
            if st.button("📄 JSON Output", use_container_width=True):
                st.session_state["view_mode"] = "JSON"

        # Display output only if receipt_obj exists
        if receipt_obj:
            if st.session_state["view_mode"] == "JSON":
                st.subheader("📄 JSON Output")
                st.json(receipt_obj.model_dump(), expanded=False)
            else:
                st.subheader("🧾 Invoice View")
                store = receipt_obj.store_info
                totals = receipt_obj.totals
                items = receipt_obj.items
                info = receipt_obj.receipt_info

                st.markdown(f"""
                **{store.name or ''}**  
                {store.address or ''}  
                {store.phone or ''}  
                **Date:** {info.date or ''}  
                **Time:** {info.time or ''}  
                ---
                """)

                item_rows = [
                    {
                        "Qty": str(item.quantity or ""),
                        "Item": str(item.name),
                        "Unit": str(item.unit_price or ""),
                        "Total": str(item.total_price or ""),
                    }
                    for item in items
                ]
                st.table(item_rows)

                st.markdown(f"""
                **Total:** {totals.total or 0}  
                **Paid:** {totals.paid or 0}  
                **Change:** {totals.change or 0}  
                **Items:** {totals.num_items or len(items)}
                ---
                """)
        else:
            st.warning("❗ No receipt data available. Try uploading again.")
else:
    st.info("📤 Upload an image file to begin.")
