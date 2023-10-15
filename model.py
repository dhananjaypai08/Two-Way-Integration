# SQL alchemy imports
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
# other imports
from pydantic import BaseModel

SQLALCHEMY_DATABASE_URL = "sqlite:///./customer.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customer"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    class Config:
        orm_mode = True
    
Base.metadata.create_all(engine)

class CustomerCreate(BaseModel):
    name: str
    email: str
    
class ResponseCustomer(BaseModel):
    id: str
    name: str
    email: str