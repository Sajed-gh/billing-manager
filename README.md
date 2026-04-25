# Billing Manager AI Agent (Vision v2)

**Billing Manager** is a high-performance AI agent that leverages **Gemini Multimodal Vision** to extract structured data from paper receipts and invoices with high precision.

---

## 🚀 Evolution: Vision v2
We have radically simplified the architecture by moving from a legacy "OCR + Text Parsing" pipeline to a **Native Multimodal** approach. This significantly improves accuracy for complex layouts, tilted images, and hand-written elements.

## ✨ Features
- **Direct Image Processing**: No more brittle local OCR dependencies.
- **Multimodal Intelligence**: Gemini "sees" the receipt structure (logos, tables, bold text) to better identify fields.
- **Structured Pydantic Output**: Guaranteed data integrity with automatic validation.
- **Streamlit Dashboard**: A clean, responsive UI for real-time extraction and visualization.

---

## 🛠 Tech Stack
- **LLM**: Google Gemini 1.5 Flash (Multimodal)
- **Frameworks**: LangChain, Pydantic, Streamlit
- **Language**: Python 3.10+

---

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Sajed-gh/billing-manager.git
   cd billing-manager
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Create a `.env` file in the root directory:
   ```text
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

---

## 🚀 Usage

### 1. Web UI (Recommended)
Run the Streamlit application for an interactive experience:
```bash
streamlit run app.py
```

### 2. CLI
Process an image directly from the terminal:
```bash
python main.py --image path/to/receipt.jpg --output results.json
```

---

## 📂 Project Structure
- `app.py`: Streamlit web interface.
- `main.py`: Core logic and CLI entry point.
- `reasoning/`: Contains the Gemini Multimodal pipeline.
- `schema.py`: Pydantic models for structured data.
- `config.py`: Configuration and API key management.