import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from schema import Receipt


load_dotenv()
api_key = os.environ["GOOGLE_API_KEY"]

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.0,api_key=api_key).with_structured_output(Receipt)

prompt = ChatPromptTemplate.from_template(
    """
    You are a data extraction assistant.

    You will receive a table (list of text rows) extracted from a scanned receipt.

    Task:
    - Infer the receipt structure: store info, items, totals, notes.

    OCR Table:
    {table_text}
    """
)

chain = prompt | model

def run(table):
    table = [row for row in table if any(cell.strip() for cell in row)]
    table_text = '\n'.join(['||'.join(row) for row in table])
    result = chain.invoke({
        "table_text": table_text,
    })

    return result


if __name__ == "__main__":
    test_table = [
        ['OjjEOAZIZA'],
        ['SAHLINE2-NUM VERT 80102080'],
        ['a BISCUIT 190G SAIDA', '1.990'],
        ['a FRAID0UX.120G PRFSID', '1', '3.100'],
        ['a Y NATURE 110G VTTALA', 'of', '0.550'],
        ['a BEURRE 1O0G NATLAL', '1', '3.420'],
        ['a CREME CHANTILLY 72G', '2.400'],
        ['a POUDRE A CREME VANI', '0.650'],
        ['a TIMBRE LOI FIN.2022', '0.100'],
        ['Total', '12.210'],
        ['Especes', '12.210'],
        ['27/06/2025 18:06 Ca1ss1er 10013 du 1439']
    ]

    receipt_obj = run(test_table)
    print(receipt_obj)
