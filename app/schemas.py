from pydantic import BaseModel, Field


class ProductInput(BaseModel):
    name: str
    description: str
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category_id: int
    image_url: str | None = None
    featured: bool = False
    rating: float = Field(default=4.5, ge=0, le=5)


class CartItem(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class CheckoutRequest(BaseModel):
    customer_name: str
    email: str
    address: str
    city: str = ""
    payment_method: str = "Card"
    items: list[CartItem]
