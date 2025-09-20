from dataclasses import dataclass
from typing import Optional

@dataclass
class Product:
    id: int
    name: str
    sku: str
    price: float
    stock: int
    reorder_level: int
    supplier: Optional[str] = None

    @property
    def is_low_stock(self) -> bool:
        return self.stock <= self.reorder_level