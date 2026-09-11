from dataclasses import dataclass


@dataclass
class Product:
    id: int | None = None
    name: str = ""
    description: str = ""
    price: float = 0.0
    stock: int = 0
    category_id: int = 1
    image_url: str | None = None
    featured: bool = False
    rating: float = 4.5


@dataclass
class Category:
    id: int | None = None
    name: str = ""
    description: str = ""
