from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import auth
from app import schemas
from app import models
from app.database import get_db
from app.models import Product

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.post("/", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):

   # if current_user.is_admin is not True:
   #     raise HTTPException(
   #      status_code=HTTP_403_FORBIDDEN,
   #       detail="sirf admin hi products add kr sakta hai"
   # )
    
    new_product = Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/", response_model=List[schemas.ProductOut])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products


@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    updated_product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):

    if current_user.is_admin is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="sirf admin hi products add kr sakta hai"
        )

    product_query = db.query(models.Product).filter(models.Product.id == product_id)
    product = product_query.first()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product nhi mila")

    for key, value in updated_product.model_dump().items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):

    if current_user.is_admin is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="sirf admin hi products dlt kr sakta hai"
        )

    product_query = db.query(models.Product).filter(models.Product.id == product_id)
    product = product_query.first()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product nhi mila")

    product_query.delete(synchronize_session=False)
    db.commit()

