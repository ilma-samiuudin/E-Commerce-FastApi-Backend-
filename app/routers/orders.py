from decimal import Decimal 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import auth, models, schemas
from app.database import get_db
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter(
    prefix="/orders",
    tags=["Orders & Checkout"]
)

@router.post("/", response_model=schemas.OrderOut, status_code=status.HTTP_201_CREATED)
def place_order(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):

    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apka shopping cart khali hai pehle isme kuch add kren"
        )

    total_price = 0.0

    for item in cart_items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="product nh mila"
            )

        if product.stock < item.quantity:  # type: ignore
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product '{product.name}' ka stock kam hai sirf {product.stock} available hai"  # FIX 1: namr -> name
            )

        total_price += product.price * item.quantity  # type: ignore
        product.stock -= item.quantity  # type: ignore

    # FIX 2: yahan se neeche ka hissa loop se bahar (dedent) kar diya
    new_order = models.Order(
        user_id=current_user.id,
        total_price=total_price,
        status="Pending"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).delete()
    db.commit()
    return new_order
    
