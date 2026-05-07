import google.generativeai as genai
from schema import Receipt
from config import api_key, MODEL_NAME
import PIL.Image

# Use Gemini 1.5 Flash (or 2.0 if available)
 # gemini-3-flash-preview might not be stable/available in SDK same way

genai.configure(api_key=api_key)

def get_gemini_schema(pydantic_model):
    """
    Converts a Pydantic model to a Gemini-compatible schema dictionary.
    Handles dereferencing, stripping 'default'/'title', and 'anyOf' -> 'nullable'.
    """
    schema = pydantic_model.model_json_schema()
    defs = schema.get("$defs", {})

    def resolve_ref(s):
        if isinstance(s, dict) and "$ref" in s:
            ref_name = s["$ref"].split("/")[-1]
            return resolve_ref(defs[ref_name])
        if isinstance(s, dict):
            return {k: resolve_ref(v) for k, v in s.items()}
        if isinstance(s, list):
            return [resolve_ref(i) for i in s]
        return s

    def clean(s):
        if not isinstance(s, dict):
            return s
        
        # 1. Handle anyOf for nullability
        if "anyOf" in s:
            types = [t for t in s["anyOf"] if t.get("type") != "null"]
            if len(types) >= 1:
                # Pick the first non-null type
                new_s = types[0].copy()
                new_s["nullable"] = True
                if "description" in s:
                    new_s["description"] = s["description"]
                s = new_s

        # 2. Strip unsupported keys while preserving structure
        res = {}
        # Keys allowed in Gemini Schema proto
        allowed_keys = ["type", "format", "description", "nullable", "enum", "required", "max_items", "min_items"]
        
        for k, v in s.items():
            if k in allowed_keys:
                res[k] = clean(v)
            elif k == "properties":
                res["properties"] = {pk: clean(pv) for pk, pv in v.items()}
            elif k == "items":
                res["items"] = clean(v)

        return res

    # Resolve all references first
    resolved = resolve_ref(schema)
    # Then clean the schema
    return clean(resolved)

# Use the robust schema generator
gemini_schema = get_gemini_schema(Receipt)

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    generation_config={
        "response_mime_type": "application/json",
        "response_schema": gemini_schema,
    }
)

system_instruction = """
You are an expert OCR and data extraction specialist.
Analyze the provided receipt image and extract all relevant information into the specified JSON format.
- Store Name, Address, and Phone.
- Receipt Number, Date (DD/MM/YYYY), and Time (HH:MM).
- All line items with quantity, name, unit price, total price, and CURRENCY (symbol or code like $, USD, EUR).
- Totals (Subtotal/Total), Paid amount, Change, and CURRENCY.
- Currency Detection: Be extremely careful to detect the currency symbol ($, €, £, etc.) or ISO code (USD, EUR, GBP, etc.). If no currency is explicitly mentioned, infer it based on the store's address or location context (e.g., if the store is in New York, it's likely USD).
If a value is not clearly visible, leave it as null. Correct minor OCR misreadings based on context.
"""

def run_multimodal(image_path):
    """
    Directly processes the image using Gemini's vision capabilities.
    """
    img = PIL.Image.open(image_path)
    
    prompt = f"{system_instruction}\n\nPlease extract the data from this receipt image."
    
    response = model.generate_content([prompt, img])
    
    # Parse the JSON response into the Receipt model
    try:
        return Receipt.model_validate_json(response.text)
    except Exception as e:
        print(f"Error parsing receipt: {e}")
        return None

def run(table):
    """
    Extracts structured data from OCR table text.
    """
    table_text = '\n'.join(['|'.join([str(cell) for cell in row]) for row in table])
    
    prompt = f"Extract structured data from this OCR table text.\n\n{table_text}"
    
    response = model.generate_content(prompt)
    
    try:
        return Receipt.model_validate_json(response.text)
    except Exception as e:
        print(f"Error parsing table: {e}")
        return None
