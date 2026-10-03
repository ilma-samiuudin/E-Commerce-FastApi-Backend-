from fastapi import FastAPI

from app.database import engine
from app import models
from app.routers import users, products, cart, orders


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Commerce Backend API", version="1.0.0")

app.include_router(users.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)

@app.get("/")
def home():
    return {"message": "Welcome to E-Commerce Backend REST API!"} 

if __name__ ==  "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
