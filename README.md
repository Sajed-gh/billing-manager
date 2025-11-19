# Billing Manager AI Agent

**Billing Manager** is an AI-powered agent that uses Google Gemini and OCR to extract information from paper bills and receipts, and then generates a structured, numeric version of those receipts.

---

## Features

- Scans invoices, receipts, and bills (photos or scans)  
- Uses **OCR** to extract raw text from documents  
- Leverages **Google Gemini** to interpret and structure the extracted data  
- Outputs a clean, structured JSON with line-items, totals, dates, vendor, units, etc.

---

## How It Works (Overview)

1. **Image Input**: You provide a photo or scan of a paper bill / receipt.  
2. **OCR Processing**: OCR engine converts the image to raw text.  
3. **LLM Interpretation**: Google Gemini processes the raw text, understanding context, semantics, and meaning.  
4. **Data Structuring**: The agent extracts key fields and outputs them in a structured numeric format.

---

## Use Cases

- Automating expense tracking from paper receipts.  
- Digitizing bills and invoices for bookkeeping.  
- Integrating with accounting software or financial dashboards.  
- Auditing and data validation on large volumes of receipt images.

---

## Tech Stack

- **OCR**: paddleocr==2.7.0 
- **LLM**: Google Gemini 2.5 
- **Programming Language / Framework**: Python, Langchain, Pydantic

---

## Installation

1. Clone the repo:

    ```bash
    git clone https://github.com/Sajed-gh/billing-manager.git
    cd billing-manager
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Setup environment variables:

    ```text
    GOOGLE_GEMINI_API_KEY=your_api_key
    ```

---

## Usage

```bash
python main.py --image path/to/receipt.jpg --output structured.json
```
