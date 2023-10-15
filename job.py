# Model imports
from model import Customer, CustomerCreate, SessionLocal, ResponseCustomer
# other imports
from typing import List, Optional
import stripe
from dotenv import load_dotenv
import os

load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")
webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

def local_to_stripe_create(customer: CustomerCreate):
    #Saving to stripe db
    try:
        response = stripe.Customer.create(
            name=customer.name,
            email=customer.email
        )
    except:
        raise Exception(f"Either email {customer.email} already exists or details are not provided")
    print("Changes saved to stripe account")
    # Saving to our db  
    try:
        db = SessionLocal()
        db_customer = Customer(id=response["id"], name=customer.name, email=customer.email)
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        db.close()
    except Exception as e:
        raise (f"Something went wrong: {str(e)}")
    print("changes saved to db")
    return response

def local_to_stripe_update(id: str, data:CustomerCreate):
    #updating in stripe
    try:
        stripe.Customer.modify(
            id,
            name=data.name
        )
    except:
        pass
    try:
        stripe.Customer.modify(
            id,
            email=data.email
        )
    except:
        pass
    print("Changes have been done from local to stripe account")
    
def local_to_stripe_delete(id: str):
    # deleting from stripe
    try:
        stripe.Customer.delete(id)
    except Exception as e:
        raise (f"Something went wrong: {str(e)}")
    print("Customer deleted from stripe account")
    