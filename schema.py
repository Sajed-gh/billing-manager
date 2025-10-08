from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time



class ReceiptItem(BaseModel):
    quantity : Optional[int] = None
    name : str
    unit_price : Optional[float] = None
    total_price : Optional[float] = None

class StoreInfo(BaseModel):
    name : Optional[str] = None
    address : Optional[str] = None
    phone : Optional[str] = None

class ReceiptInfo(BaseModel):
    receipt_number : Optional[str] = None
    date : Optional[str] = None
    time : Optional[str] = None
    cachier : Optional[str] = None

class ReceiptTotal(BaseModel):
    total: Optional[float] = None
    paid : Optional[float] = None
    change : Optional[float] = None
    num_items : Optional[int] = None

class Receipt(BaseModel):
    store_info: StoreInfo
    receipt_info : ReceiptInfo
    items : List[ReceiptItem]
    totals : ReceiptTotal
    note : Optional[List[str]] = []
