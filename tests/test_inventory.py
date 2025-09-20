import os
import tempfile
import pytest

# Use a temp CSV for tests
tmp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
os.environ["INVENTORY_CSV_PATH"] = tmp_csv.name

from inventory import inventory as inv  # noqa: E402
from inventory.errors import NegativeStockError  # noqa: E402

@pytest.fixture(autouse=True, scope="function")
def setup_csv():
    # reset file each test
    inv.set_current_path(os.environ["INVENTORY_CSV_PATH"])
    try:
        os.remove(inv.current_path())
    except FileNotFoundError:
        pass
    inv.init_storage()
    yield

def test_stock_adjustment_prevents_negative():
    pid = inv.create_product(name="Test", sku="ABC-1234", stock=2, reorder_level=1)
    inv.adjust_stock(pid, -2)
    p = inv.get_product(pid)
    assert p.stock == 0
    with pytest.raises(NegativeStockError):
        inv.adjust_stock(pid, -1)

def test_increment_and_low_stock_flag():
    pid = inv.create_product(name="Widget", sku="WID-1000", stock=1, reorder_level=5)
    p = inv.get_product(pid)
    assert p.is_low_stock is True
    inv.adjust_stock(pid, +10)
    p = inv.get_product(pid)
    assert p.stock == 11
    assert p.is_low_stock is False