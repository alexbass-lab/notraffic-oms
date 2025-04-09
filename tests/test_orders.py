import pytest
import requests
from pymongo import MongoClient

BASE_URL = "http://localhost:8000/orders"

# Create test data
test_order = {
    "user_id": "u12345",
    "items": [
        {"product_id": "p001", "name": "Laptop", "price": 1200, "quantity": 1},
        {"product_id": "p002", "name": "Mouse", "price": 25, "quantity": 2}
    ],
    "total_price": 1250,
    "status": "Pending"
}

def test_create_order():
    response = requests.post(BASE_URL, json=test_order)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "Pending"
    test_order["_id"] = data["_id"]

def test_get_order():
    response = requests.get(f"{BASE_URL}/{test_order['_id']}")
    assert response.status_code == 200
    assert response.json()["total_price"] == test_order["total_price"]

def test_update_order_status():
    response = requests.patch(f"{BASE_URL}/{test_order['_id']}", json={"status": "Shipped"})
    assert response.status_code == 200
    assert response.json()["status"] == "Shipped"

def test_delete_order():
    response = requests.delete(f"{BASE_URL}/{test_order['_id']}")
    assert response.status_code == 204
