# kafka imports
from kafka import KafkaConsumer
# Model imports
from model import Customer, CustomerCreate, SessionLocal, ResponseCustomer

# Create Kafka consumer for local to Stripe events
consumer_local_to_stripe = KafkaConsumer('local_and_to_stripe', bootstrap_servers='localhost:9092', 
                                         value_deserializer=lambda v: v.decode('utf-8'))

while True:
    print("Consumer service running....")
    for message in consumer_local_to_stripe:
        key = message.key
        value = message.value
        print(f"Incoming request: {key} and value={value}")
        if key == 'customer_created':
            #Saving to stripe db
            customer = value
            try:
                response = stripe.Customer.create(
                    name=customer['name'],
                    email=customer['email']
                )
            except:
                raise Exception(f"Either email {customer.email} already exists or details are not provided")
            print("Changes saved to stripe account")
    
            # Saving to our db  
            try:
                db = SessionLocal()
                db_customer = ResponseCustomer(id=response["id"], name=customer['name'], email=customer['email'])
                db.add(db_customer)
                db.commit()
                db.refresh(db_customer)
                db.close()
            except Exception as e:
                raise (f"Something went wrong: {str(e)}")
    
            print("changes saved to db")
            print(customer)

        elif key == 'customer_updated':
            #updating in stripe
            data = value
            id = data["id"]
            try:
                stripe.Customer.modify(
                    id,
                    name=data['name']
                )
            except:
                pass
            try:
                stripe.Customer.modify(
                    id,
                    email=data['email']
                )
            except:
                pass
            print("Changes have been done from local to stripe account")
    
            #updating in db
            try:
                db = SessionLocal()
                customer = db.query(ResponseCustomer).filter_by(id=id).first()
                customer.name = data['name']
                customer.email = data['email']
                db.commit()
                db.refresh(customer)
                db.close()
            except Exception as e:
                raise (f"Something went wrong: {str(e)}")
            print(customer)

        elif key == 'customer_deleted':
            id = value
            # deleting from stripe
            try:
                stripe.Customer.delete(id)
            except Exception as e:
                raise (f"Something went wrong: {str(e)}")
            print("Customer deleted from stripe account")
            
            # deleting from db
            try:
                
                db = SessionLocal()
                customer = db.query(ResponseCustomer).filter_by(id=id).first()
                db.delete(customer)
                db.commit()
                db.close()
            except Exception as e:
                raise (f"Something went wrong: {str(e)}")
            print("Customer deleted from local db")
            