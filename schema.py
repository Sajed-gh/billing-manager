from pydantic import BaseModel, Field
from typing import Optional, List


class ReceiptItem(BaseModel):
    quantity: Optional[int] = Field(
        None, description="Number of units purchased for this item"
    )
    name: str = Field(
        ..., description="Name or description of the purchased item"
    )
    unit_price: Optional[float] = Field(
        description="Price per unit of the item"
    )
    total_price: Optional[float] = Field(
        None, description="Total price for this line item (quantity × unit_price if available)"
    )


class StoreInfo(BaseModel):
    name: Optional[str] = Field(
        None, description="Name of the store or merchant"
    )
    address: Optional[str] = Field(
        None, description="Physical address of the store, if available"
    )
    phone: Optional[str] = Field(
        None, description="Contact phone number of the store"
    )


class ReceiptInfo(BaseModel):
    receipt_number: Optional[str] = Field(
        None, description="Unique identifier or number of the receipt"
    )
    date: Optional[str] = Field(
        None, description="Date of the transaction in DD/MM/YYYY format"
    )
    time: Optional[str] = Field(
        None, description="Time of the transaction in HH:MM format"
    )
    cachier: Optional[str] = Field(
        None, description="Name or ID of the cashier who processed the transaction"
    )


class ReceiptTotal(BaseModel):
    total: Optional[float] = Field(
        None, description="Total amount of the receipt before any discounts or change"
    )
    paid: Optional[float] = Field(
        None, description="Amount actually paid by the customer"
    )
    change: Optional[float] = Field(
        None, description="Change returned to the customer, if any"
    )
    num_items: Optional[int] = Field(
        None, description="Total number of items on the receipt"
    )


class Receipt(BaseModel):
    store_info: StoreInfo = Field(..., description="Information about the store")
    receipt_info: ReceiptInfo = Field(..., description="Metadata about the receipt")
    items: List[ReceiptItem] = Field(..., description="List of all purchased items")
    totals: ReceiptTotal = Field(..., description="Summary totals of the receipt")
    note: Optional[List[str]] = Field(
        default=[], description="Any additional notes or comments on the receipt"
    )
