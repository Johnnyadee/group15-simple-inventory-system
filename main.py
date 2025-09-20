from ui.app import InventoryApp
from inventory import inventory as inv

def main():
    # Initialize storage (loads from INVENTORY_CSV_PATH or products.csv if present)
    inv.init_storage()
    app = InventoryApp()
    app.run()

if __name__ == "__main__":
    main()