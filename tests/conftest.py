import pytest
from pymongo import MongoClient

@pytest.fixture(scope="session")
def mongo_client():
    client = MongoClient("mongodb://localhost:27017/")
    yield client
    client.close()

@pytest.fixture(scope="session", autouse=True)
def clean_orders_collection(mongo_client):
    db = mongo_client["oms_db"]
    db.orders.delete_many({})
