import re

# Simple SKU check: 4-20 chars, uppercase letters, digits, hyphen
SKU_PATTERN = re.compile(r"^[A-Z0-9-]{4,20}$")

def validate_sku(sku: str) -> bool:
    if not sku:
        return False
    return bool(SKU_PATTERN.fullmatch(sku.strip().upper()))