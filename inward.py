# redis imports
import redis
# Model imports
from model import Customer, CustomerCreate, SessionLocal, ResponseCustomer
# Other imports
import json
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

# Redis Connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

stripe.api_key = os.getenv("STRIPE_API_KEY")

print("Consumer service Inwards is running....")
while True:
    
    task = redis_client.rpop("inward")
    if task:
        customer = json.loads(task)
            
        if customer['key'] == 'customer_created':
            try:
                db = SessionLocal()
                db_customer = Customer(id=customer["id"], name=customer["name"], email=customer["email"])
                db.add(db_customer)
                db.commit()
                db.refresh(db_customer)
                db.close()
                print(db_customer)
                print('customer created')
            except:
                print("Something went wrong")
                
        if customer['key'] == 'customer_updated':
            try:
                db = SessionLocal()
                db_customer = db.query(Customer).filter_by(id=customer["id"]).first()
                db_customer.name = customer["name"]
                db_customer.email = customer["email"]
                db.commit()
                db.refresh(customer)
                db.close()
                print(db_customer)
                print('customer updated')
            except:
                print("Something went wrong")
            
        if customer['key'] == 'customer_deleted':
            try:
                db = SessionLocal()
                db_customer = db.query(Customer).filter_by(id=customer["id"]).first()
                db.delete(db_customer)
                db.commit()
                db.close()
                print('customer deleted')
            except:
                print("Something went wrong")
