from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import SessionLocal, engine
import database_models
from models import Product

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"]
)
 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


database_models.Base.metadata.create_all(bind=engine)

products = [ { "id": 1, "name": "Laptop", "description": "14-inch laptop with 16GB RAM", "price": 75000, "quantity": 10 }, 
            { "id": 2, "name": "Smartphone", "description": "5G Android smartphone", "price": 30000, "quantity": 25 }, 
            { "id": 3, "name": "Headphones", "description": "Noise cancelling headphones", "price": 8000, "quantity": 40 },
            { "id": 4, "name": "Keyboard", "description": "Mechanical keyboard", "price": 4500, "quantity": 15 }, 
            { "id": 5, "name": "Mouse", "description": "Wireless mouse", "price": 1500, "quantity": 30 },
            { "id": 6, "name": "Monitor", "description": "27-inch Full HD monitor", "price": 18000, "quantity": 8 } 
            ]

def init_db():
    db = SessionLocal()

    existing = db.query(database_models.Product).first()
    if existing:
        db.close()
        return

    for product in products:
        db.add(database_models.Product(**product))

    db.commit()
    db.close()


init_db() 

@app.get("/products/")
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(database_models.Product).all()
    return products


@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    prod = db.query(database_models.Product).filter(database_models.Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod


# Pydantic models for request validation
class Product(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: int
    quantity: int


class ProductCreate(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: int
    quantity: int


@app.post("/products/", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate):
    db = SessionLocal()

    db_product = database_models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        quantity=product.quantity
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    db.close()

    return db_product



class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    quantity: Optional[int] = None


@app.put("/products/{product_id}")
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    db_prod = db.query(database_models.Product).filter(database_models.Product.id == product_id).first()
    if not db_prod:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.name is not None:
        db_prod.name = product.name
    if product.description is not None:
        db_prod.description = product.description
    if product.price is not None:
        db_prod.price = product.price
    if product.quantity is not None:
        db_prod.quantity = product.quantity
    db.add(db_prod)
    db.commit()
    db.refresh(db_prod)
    return db_prod


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_prod = db.query(database_models.Product).filter(database_models.Product.id == product_id).first()
    if not db_prod:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_prod)
    db.commit()
    return
