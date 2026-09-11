from pydantic import BaseModel, Field, field_validator


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
    card_number: str | None = None
    card_holder: str | None = None
    card_last4: str | None = None
    items: list[CartItem]

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@", 1)[1]:
            raise ValueError("Invalid email address")
        return value.strip().lower()


class OrderStatusUpdate(BaseModel):
    fulfillment_status: str = Field(default="processing")
