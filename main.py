# FastAPI imports
from fastapi import FastAPI, Request

# Model imports
from model import Customer, CustomerCreate, SessionLocal, ResponseCustomer

# redis import
import redis

# other imports
from typing import List, Optional
import uvicorn
import stripe
from dotenv import load_dotenv
import os
import json

load_dotenv()
app = FastAPI()

# Redis Connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

stripe.api_key = os.getenv("STRIPE_API_KEY")
webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

# Handle Incoming requests from Stripe
@app.post("/stripe/webhook")
async def stripe_webhook(request: Request, event_id: Optional[str] = None):
    """ This endpoint is a webhook that detects modifications from stripe account and updates to our Local DB using Redis Queue"""
    payload = await request.body()
    sign_headers = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sign_headers, webhook_secret
        )
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Handle the specific events
    if event.type == "customer.created":
        customer = event.data.object
        # Serialize the task, including parameters, to JSON
        customer['key'] = 'customer_created'
        task = json.dumps(customer)
        # Add the task to the queue
        redis_client.lpush("inward", task)
        print("Customer Creation request from stripe was sent to Redis Queue")
    
    if event.type == "customer.updated":
        customer = event.data.object
        customer['key'] = 'customer_updated'
        task = json.dumps(customer)
        # Add the task to the queue
        redis_client.lpush("inward", task)
        print("Customer Updation request sent to Redis")
        
    if event.type == "customer.deleted":
        customer = event.data.object
        customer = {"id": customer['id']}
        customer['key'] = 'customer_deleted'
        task = json.dumps(customer)
        # Add the task to the queue
        redis_client.lpush("inward", task)
        print("Customer deletion request sent to Redis")

# API routes
@app.post("/stripe/customers", response_model=dict)
async def create_customer(customer: CustomerCreate):
    """Create a new customer on Local + stripe

    Args:
        customer (CustomerCreate): model details of customer

    Returns:
        dict: Status of the tasks added to the queue
    """
    # Serialize the task, including parameters, to JSON
    new_customer = customer.dict()
    new_customer['key'] = 'customer_created'
    task = json.dumps(new_customer)
    # Add the task to the queue
    redis_client.lpush("outward", task)
    return {"message": "Customer Creation request sent to Redis Queue"}

@app.get("/stripe/customers", response_model=List[ResponseCustomer])
async def get_customer():
    """Get all the customers

    Returns:
        List[ResponseCustomer]: list details of the retrieved customer
    """
    db = SessionLocal()
    customers = db.query(Customer).all()
    db.close()
    return customers

@app.get("/stripe/customers/get", response_model=ResponseCustomer)
async def get_specific_customer(id: str):
    """ Get a specific customer

    Args:
        id (str): Customer ID

    Returns:
        ResponseCustomer: details of the retrieved customer
    """
    try:
        db = SessionLocal()
        customer = db.query(Customer).filter_by(id=id).first()
        db.close()
    except Exception as e:
        print(f"Something went wrong: {str(e)}")
    return customer

@app.put("/stripe/customers", response_model=dict)
async def update_customer(id: str, data: CustomerCreate):
    """ Updating a customer in strip + local

    Args:
        id (str): customer ID
        data (CustomerCreate): Customer model Details

    Returns:
        dict: Status of the tasks added to the queue
    """
    customer = data.dict()
    customer['id'] = id
    customer['key'] = 'customer_updated'
    task = json.dumps(customer)
    # Add the task to the queue
    redis_client.lpush("outward", task)
    return {"message": "Customer Updation request sent to Redis"}

@app.delete("/stripe/customers", response_model=dict)
async def delete_customer(id: str):
    """ Deleting customer from local + stripe

    Args:
        id (str): customer_id

    Returns:
        str: success message
    """
    customer = {"id": id}
    customer['key'] = 'customer_deleted'
    task = json.dumps(customer)
    # Add the task to the queue
    redis_client.lpush("outward", task)
    return {"message": "Customer deletion request sent to Redis"}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
    