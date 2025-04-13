from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
from pymongo import MongoClient
import uvicorn

app = FastAPI(title="Order Management System API")

# --- MongoDB Setup ---
client = MongoClient("mongodb://localhost:27017/")

db = client["oms_db"]
orders_collection = db["orders"]

# --- Helper to convert Mongo ObjectId ---
def serialize_order(order):
    order["_id"] = str(order["_id"])
    return order

# --- Models ---
class Item(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int

class Order(BaseModel):
    user_id: str
    items: List[Item]
    total_price: float
    status: str = Field(..., description="Order status (e.g., pending, shipped, delivered)")

class StatusUpdate(BaseModel):
    status: str

# --- API Routes ---
@app.post("/orders", status_code=201)
def create_order(order: Order):
    order_dict = order.dict()
    result = orders_collection.insert_one(order_dict)
    order_dict["_id"] = str(result.inserted_id)
    return order_dict

@app.get("/orders", response_model=List[dict])
def list_orders():
    orders = list(orders_collection.find())
    return [serialize_order(order) for order in orders]

@app.get("/orders/{order_id}")
def get_order(order_id: str):
    try:
        order = orders_collection.find_one({"_id": ObjectId(order_id)})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return serialize_order(order)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid order ID")

@app.patch("/orders/{order_id}")
def update_order_status(order_id: str, update: StatusUpdate):
    result = orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": update.status}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    updated_order = orders_collection.find_one({"_id": ObjectId(order_id)})
    return serialize_order(updated_order)

@app.delete("/orders/{order_id}", status_code=204)
def delete_order(order_id: str):
    result = orders_collection.delete_one({"_id": ObjectId(order_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return

# --- Run server if executed directly ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
