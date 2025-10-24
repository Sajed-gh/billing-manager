from langchain_google_genai import ChatGoogleGenerativeAI
from schema import Receipt
from config import api_key



model = ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.2,api_key=api_key).with_structured_output(Receipt)


system_instruction = """
You are a data extraction assistant.
Extract structured data from receipt tables.
Correct only obvious OCR errors.
Infer missing quantities if obvious.
Ignore irrelevant lines.
"""


def run(table):
    table = [row for row in table if any(str(cell).strip() for cell in row)]
    table_text = '\n'.join(['|'.join([str(cell) for cell in row]) for row in table])

    result = model.invoke([
    {"role": "system", "content": system_instruction},
    {"role": "user", "content": table_text}
])

    return result


if __name__ == "__main__":
    test_table = [
        ['OjjEOAZIZA'],
        ['SAHLINE2-NUM VERT 80102080'],
        ['a BISCUIT 190G SAIDA', '1.99'],
        ['a FRAID0UX.120G PRFSID', '1', '3.10'],
        ['a Y NATURE 110G VTTALA', 'of', '0.55'],
        ['a BEURRE 1O0G NATLAL', '1', '3.42'],
        ['a CREME CHANTILLY 72G', '2.40'],
        ['a POUDRE A CREME VANI', '0.65'],
        ['a TIMBRE LOI FIN.2022', '0.10'],
        ['Total', '12.21'],
        ['Especes', '12.21'],
        ['27/06/2025 18:06 Ca1ss1er 10013 du 1439']
    ]

    receipt_obj = run(test_table)
    print(receipt_obj)
