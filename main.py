# FastAPI imports
from fastapi import FastAPI, Request

# Model imports
from model import Customer, CustomerCreate, SessionLocal, ResponseCustomer

# other imports
from typing import List, Optional
import uvicorn
import stripe
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

stripe.api_key = os.getenv("STRIPE_API_KEY")
webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

# Handle Incoming requests from Stripe
@app.post("/stripe/webhook")
async def stripe_webhook(request: Request, event_id: Optional[str] = None):
    payload = await request.body()
    sign_headers = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sign_headers, webhook_secret
        )
    except Exception as e:
        return {"error": f"Error: {str(e)}"}
    
    # Handle the specific events
    if event.type == "customer.created":
        customer = event.data.object
        db = SessionLocal()
        db_customer = Customer(id=customer["id"], name=customer["name"], email=customer["email"])
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        db.close()
    
    if event.type == "customer.updated":
        customer = event.data.object
        db = SessionLocal()
        db_customer = db.query(Customer).filter_by(id=customer["id"]).first()
        db_customer.name = customer["name"]
        db_customer.email = customer["email"]
        db.commit()
        db.refresh(customer)
        db.close()
        
    if event.type == "customer.deleted":
        customer = event.data.object
        db = SessionLocal()
        db_customer = db.query(Customer).filter_by(id=customer["id"]).first()
        db.delete(db_customer)
        db.commit()
        db.close()

# API routes
@app.post("/stripe/customers", response_model=ResponseCustomer)
async def create_customer(customer: CustomerCreate):
    #Saving to stripe db
    response = stripe.Customer.create(
        name=customer.name,
        email=customer.email
    )
    
    # Saving to our db
    db = SessionLocal()
    db_customer = Customer(id=response["id"], name=customer.name, email=customer.email)
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

@app.get("/stripe/customers/get", response_model=ResponseCustomer)
async def get_specific_customer(id: str):
    db = SessionLocal()
    customer = db.query(Customer).filter_by(id=id).first()
    db.close()
    return customer

@app.put("/stripe/customers", response_model=ResponseCustomer)
async def update_customer(id: str, data: CustomerCreate):
    #updating in stripe
    stripe.Customer.modify(
        id,
        name=data.name
    )
    stripe.Customer.modify(
        id,
        email=data.email
    )
    
    #updating in db
    db = SessionLocal()
    customer = db.query(Customer).filter_by(id=id).first()
    customer.name = data.name
    customer.email = data.email
    db.commit()
    db.refresh(customer)
    db.close()
    return customer

@app.delete("/stripe/customers", response_model=str)
async def delete_customer(id: str):
    # deleting from stripe
    stripe.Customer.delete(id)
    
    # deleting from db
    db = SessionLocal()
    customer = db.query(Customer).filter_by(id=id).first()
    db.delete(customer)
    db.commit()
    db.close()
    return "Customer deleted"

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
    