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

def main():
    """ Main outward sync from Local DB to stripe that consumes tasks from the task queue"""
    print("Consumer service Outwards is running....")
    while True:
        task = redis_client.rpop("outward")
        if task:
            customer = json.loads(task)
            print(customer)
            if customer['key'] == 'customer_created':
                #Saving to stripe db
                try:
                    response = stripe.Customer.create(
                        name=customer['name'],
                        email=customer['email']
                    )
                except:
                    mail = customer['email']
                    print(f"Either email {mail} already exists or details are not provided")
                print("Changes saved to stripe account")
                
                # Saving to our db  
                try:
                    db = SessionLocal()
                    db_customer = Customer(id=response["id"], name=customer['name'], email=customer['email'])
                    db.add(db_customer)
                    db.commit()
                    db.refresh(db_customer)
                    db.close()
                except Exception as e:
                    print(f"Something went wrong: {str(e)}")
                
                print("changes saved to db")
                print(customer)

            elif customer['key'] == 'customer_updated':
                #updating in stripe
                id = customer["id"]
                try:
                    stripe.Customer.modify(
                        id,
                        name=customer['name']
                    )
                except:
                    pass
                try:
                    stripe.Customer.modify(
                        id,
                        email=customer['email']
                    )
                except:
                    pass
                print("Changes have been done from local to stripe account")
                
                #updating in db
                try:
                    db = SessionLocal()
                    new_customer = db.query(Customer).filter_by(id=id).first()
                    new_customer.name = customer['name']
                    new_customer.email = customer['email']
                    db.commit()
                    db.refresh(new_customer)
                    db.close()
                except:
                    print(f"Something went wrong")
                print(new_customer)
                print('Changes saved in db')

            elif customer['key'] == 'customer_deleted':
                id = customer['id']
                # deleting from stripe
                try:
                    stripe.Customer.delete(id)
                except Exception as e:
                    print(f"Something went wrong: {str(e)}")
                print("Customer deleted from stripe account")
                        
                # deleting from db
                try:        
                    db = SessionLocal()
                    curr_customer = db.query(Customer).filter_by(id=id).first()
                    db.delete(curr_customer)
                    db.commit()
                    db.close()
                except Exception as e:
                    print(f"Something went wrong: {str(e)}")
                print("Customer deleted from local db")

if __name__ == '__main__':
    main()