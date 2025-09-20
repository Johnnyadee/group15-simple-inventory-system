import csv
import os
import tempfile
from typing import List, Optional
from .models import Product
from .sku import validate_sku
from .errors import NegativeStockError, InvalidSKUError

_HEADERS = ["id", "name", "sku", "price", "stock", "reorder_level", "supplier"]
_DEFAULT_PATH = "products.csv"
_ENV_PATH = "INVENTORY_CSV_PATH"

_products: list[Product] = []
_next_id: int = 1
_current_path: str = os.getenv(_ENV_PATH, _DEFAULT_PATH)

def init_storage():
    path = os.getenv(_ENV_PATH, _DEFAULT_PATH)
    load_from(path if os.path.exists(path) else None)

def current_path() -> str:
    return _current_path

def set_current_path(path: str):
    global _current_path
    _current_path = path

def _update_next_id():
    global _next_id
    _next_id = (max((p.id for p in _products), default=0) + 1)

def load_from(path: Optional[str]):
    """Load products from CSV (or start empty if path is None)."""
    global _products
    if path is None:
        _products = []
        _update_next_id()
        return

    loaded: list[Product] = []
    try:
        with open(path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            has_id = "id" in (reader.fieldnames or [])
            for row in reader:
                try:
                    pid = int(row["id"]) if has_id and row.get("id") else None
                    name = (row.get("name") or "").strip()
                    sku = (row.get("sku") or "").strip().upper()
                    price = float(row.get("price") or 0)
                    stock = int(row.get("stock") or 0)
                    reorder_level = int(row.get("reorder_level") or 0)
                    supplier = (row.get("supplier") or "").strip() or None
                except Exception:
                    continue
                if not name or not validate_sku(sku):
                    continue
                loaded.append(Product(
                    id=pid or 0,
                    name=name,
                    sku=sku,
                    price=price,
                    stock=stock,
                    reorder_level=reorder_level,
                    supplier=supplier
                ))
    except FileNotFoundError:
        loaded = []

    # Fix ids if missing
    next_id = 1
    for p in loaded:
        if not p.id or p.id < 0:
            p.id = next_id
            next_id += 1
        else:
            next_id = max(next_id, p.id + 1)

    _products = loaded
    set_current_path(path)
    _update_next_id()

def save_to(path: Optional[str] = None):
    """Write products to CSV (temp file then replace)."""
    target = path or _current_path or _DEFAULT_PATH
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    dir_name = os.path.dirname(target) or "."
    with tempfile.NamedTemporaryFile("w", delete=False, dir=dir_name, newline="", encoding="utf-8") as tmp:
        writer = csv.DictWriter(tmp, fieldnames=_HEADERS)
        writer.writeheader()
        for p in sorted(_products, key=lambda x: x.name.lower()):
            writer.writerow({
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "price": f"{float(p.price):.2f}",
                "stock": int(p.stock),
                "reorder_level": int(p.reorder_level),
                "supplier": p.supplier or "",
            })
        temp_name = tmp.name
    os.replace(temp_name, target)
    set_current_path(target)

def export_csv(path: str):
    save_to(path)

def import_csv(path: str) -> int:
    """Merge from CSV by SKU; overwrite fields and stock."""
    count = 0
    try:
        with open(path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get("name") or "").strip()
                sku = (row.get("sku") or "").strip().upper()
                if not name or not validate_sku(sku):
                    continue
                price = float(row.get("price") or 0)
                stock = int(row.get("stock") or 0)
                reorder_level = int(row.get("reorder_level") or 0)
                supplier = (row.get("supplier") or "").strip() or None
                existing = _find_by_sku(sku)
                if existing:
                    existing.name = name
                    existing.price = price
                    existing.stock = stock
                    existing.reorder_level = reorder_level
                    existing.supplier = supplier
                else:
                    _add_new(name=name, sku=sku, price=price, stock=stock, reorder_level=reorder_level, supplier=supplier)
                count += 1
        save_to()
        return count
    except Exception:
        return 0

def list_products() -> List[Product]:
    return list(sorted(_products, key=lambda p: p.name.lower()))

def list_low_stock() -> List[Product]:
    return [p for p in list_products() if p.is_low_stock]

def get_product(pid: int) -> Optional[Product]:
    for p in _products:
        if p.id == pid:
            return p
    return None

def _find_by_sku(sku: str) -> Optional[Product]:
    su = sku.strip().upper()
    for p in _products:
        if p.sku.upper() == su:
            return p
    return None

def _add_new(name: str, sku: str, price: float, stock: int, reorder_level: int, supplier: Optional[str]) -> Product:
    global _next_id
    new = Product(
        id=_next_id,
        name=name.strip(),
        sku=sku.strip().upper(),
        price=float(price),
        stock=int(stock),
        reorder_level=int(reorder_level),
        supplier=(supplier or None),
    )
    _products.append(new)
    _next_id += 1
    return new

def create_product(name: str, sku: str, price: float = 0.0, stock: int = 0, reorder_level: int = 0, supplier: Optional[str] = None) -> int:
    if not validate_sku(sku):
        raise InvalidSKUError("SKU must be 4-20 chars (A-Z, 0-9, -)")
    if stock < 0 or reorder_level < 0:
        raise ValueError("Stock and reorder level must be >= 0")
    if _find_by_sku(sku):
        raise ValueError("SKU already exists")
    p = _add_new(name, sku, price, stock, reorder_level, supplier)
    save_to()
    return p.id

def update_product(pid: int, *, name: Optional[str] = None, sku: Optional[str] = None, price: Optional[float] = None, reorder_level: Optional[int] = None, supplier: Optional[str] = None):
    p = get_product(pid)
    if not p:
        raise ValueError("Product not found")
    if sku is not None:
        su = sku.strip().upper()
        if not validate_sku(su):
            raise InvalidSKUError("SKU failed validation")
        other = _find_by_sku(su)
        if other and other.id != pid:
            raise ValueError("Another product already uses this SKU")
        p.sku = su
    if name is not None:
        p.name = name.strip()
    if price is not None:
        p.price = float(price)
    if reorder_level is not None:
        if reorder_level < 0:
            raise ValueError("Reorder level must be >= 0")
        p.reorder_level = int(reorder_level)
    if supplier is not None:
        p.supplier = supplier.strip() or None
    save_to()

def delete_product(pid: int):
    global _products
    before = len(_products)
    _products = [p for p in _products if p.id != pid]
    if len(_products) == before:
        raise ValueError("Product not found")
    save_to()

def adjust_stock(pid: int, delta: int):
    if not isinstance(delta, int):
        raise ValueError("Delta must be an integer")
    p = get_product(pid)
    if not p:
        raise ValueError("Product not found")
    new_stock = p.stock + delta
    if new_stock < 0:
        raise NegativeStockError("Stock cannot be negative")
    p.stock = new_stock
    save_to()