from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import auth, models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/cart",
    tags=["Shopping Cart"]
)

@router.post("/", response_model=schemas.CartItemOut, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    item: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):

    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product nhi mila")

    if product.stock < item.quantity: # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Afsoos Sirf {product.stock} item stock me bache hai"
        )

    existing_cart_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id,
        models.CartItem.product_id == item.product_id
    ).first()
    
    if existing_cart_item:
        existing_cart_item.quantity += item.quantity # type: ignore
        db.commit()
        db.refresh(existing_cart_item)
        return existing_cart_item

    new_cart_item = models.CartItem(
        user_id=current_user.id,
        product_id=item.product_id,
        quantity=item.quantity
    )

    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)
    return new_cart_item

@router.get("/", response_model=List[schemas.CartItemOut])
def view_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):

    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()
    return cart_items

