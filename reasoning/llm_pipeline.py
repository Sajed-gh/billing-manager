import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from schema import Receipt
from config import api_key

# Use Gemini 3 Flash Preview
MODEL_NAME = "gemini-3-flash-preview"

model = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    temperature=0,
    api_key=api_key
).with_structured_output(Receipt)

system_instruction = """
You are an expert OCR and data extraction specialist.
Analyze the provided receipt image and extract all relevant information into the specified JSON format.
- Store Name, Address, and Phone.
- Receipt Number, Date (DD/MM/YYYY), and Time (HH:MM).
- All line items with quantity, name, unit price, total price, and CURRENCY (symbol or code like $, USD, EUR).
- Totals (Subtotal/Total), Paid amount, Change, and CURRENCY.
If a value is not clearly visible, leave it as null. Correct minor OCR misreadings based on context.
"""

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def run_multimodal(image_path):
    """
    Directly processes the image using Gemini's vision capabilities.
    """
    base64_image = encode_image(image_path)
    
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": "Please extract the data from this receipt image.",
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            },
        ]
    )
    
    result = model.invoke([
        SystemMessage(content=system_instruction),
        message
    ])
    
    return result

# Keeping the old run function for compatibility during migration if needed
def run(table):
    table_text = '\n'.join(['|'.join([str(cell) for cell in row]) for row in table])
    
    result = model.invoke([
        SystemMessage(content="Extract structured data from this OCR table text."),
        HumanMessage(content=table_text)
    ])
    return result