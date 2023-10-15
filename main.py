# FastAPI imports
from fastapi import FastAPI

# Model imports
from model import Customer, CustomerCreate, SessionLocal, ResponseCustomer

# other imports
from typing import List
import uvicorn
import stripe
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

stripe.api_key = os.getenv("STRIPE_API_KEY")

# API routes
@app.post("/stripe/customers", response_model=ResponseCustomer)
async def create_customer(customer: CustomerCreate):
    db = SessionLocal()
    db_customer = Customer(name=customer.name, email=customer.email)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    db.close()
    return db_customer

@app.get("/stripe/customers", response_model=List[ResponseCustomer])
async def get_customer():
    db = SessionLocal()
    customers = db.query(Customer).all()
    db.close()
    return customers

@app.get("/stripe/customers", response_model=ResponseCustomer)
async def get_customer(id: int):
    db = SessionLocal()
    customer = db.query(Customer).filter_by(id=id).first()
    db.close()
    return customer

@app.put("/stripe/customers", response_model=ResponseCustomer)
async def update_customer(id: int, data: CustomerCreate):
    db = SessionLocal()
    customer = db.query(Customer).filter_by(id=id).first()
    customer.name = data.name
    customer.email = data.email
    db.commit()
    db.refresh(customer)
    db.close()
    return customer

@app.delete("/stripe/customers", response_model=str)
async def delete_customer(id: int):
    db = SessionLocal()
    customer = db.query(Customer).filter_by(id=id).first()
    db.delete(customer)
    db.commit()
    db.close()
    return "Customer deleted"

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
    