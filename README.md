# Simple Inventory System (CSV-only Tkinter Desktop App)

## Overview

This is a simple desktop application to manage a product inventory, designed for educational purposes and student assignments. The app lets you track products, stock quantities, suppliers, and automatically highlights items that are low in stock. It uses a CSV file for all data storage—no database is required, and the code is kept simple and easy to understand.

The user interface is built with Python's Tkinter library. All product data is stored in a single CSV file (`products.csv` by default), which makes it easy to back up, share, or edit outside of the app.

---

## Features

- **Product Management**
  - Add new products with name, SKU, price, supplier, initial stock, and reorder level
  - Edit existing products
  - Delete products
  - Unique SKU enforcement

- **Stock Operations**
  - Adjust stock quantity up or down
  - Prevents negative stock (app will show an error if you try)

- **Low Stock Alerts**
  - Items at or below their reorder level are highlighted (yellow for low, red for zero)
  - "Show Low Stock" button to list only items needing reorder
  - Status bar shows count of low-stock items

- **CSV Import/Export**
  - Save and load inventory data from CSV files
  - Merge/import products from another CSV (matches by SKU)
  - Export your inventory to CSV for backup or sharing

- **SKU Validation**
  - SKU must be 4-20 characters, using only uppercase letters (A-Z), digits (0-9), and hyphens (-)
  - Invalid SKUs will be rejected

- **Testing**
  - Comes with pytest-based automated tests for stock operations and low-stock alerts

- **Sample Data**
  - Includes `products.csv` with example products so you can see the app in action immediately

---

## How to Run

### Prerequisites

- **Python 3.10 or newer**  
  Tkinter is included with most Python installations.  
  - On Linux, if you get errors about Tkinter missing, install with:  
    `sudo apt-get install python3-tk`

### Steps

1. **Clone or Download the Project**  
   Place all the files (including `main.py`, `requirements.txt`, and `products.csv`) in the same folder.

2. **Install pytest for running tests (optional)**  

   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Application**  
   Open your terminal or command prompt, navigate to the project folder, and run:
   - On Windows:

     ```bash
     python main.py
     ```

   - On macOS/Linux:

     ```bash
     python3 main.py
     ```

   The graphical app will open and load the sample `products.csv`.

4. **Optional: Use a Different CSV File**  
   You can set the file to use with an environment variable:
   - Windows CMD:

     ```bat
     set INVENTORY_CSV_PATH=C:\path\to\yourfile.csv
     python main.py
     ```

   - PowerShell:

     ```powershell
     $env:INVENTORY_CSV_PATH="C:\path\to\yourfile.csv"
     python main.py
     ```

   - macOS/Linux:

     ```bash
     export INVENTORY_CSV_PATH=/path/to/yourfile.csv
     python3 main.py
     ```

5. **Run Tests (optional, recommended for grading and assignment checks)**

   ```bash
   pytest
   ```

---

## CSV File Format

The CSV file used for storage has these columns:

```csv
id,name,sku,price,stock,reorder_level,supplier
```

- `id` is auto-managed by the app (you don't need to edit it)
- `sku` must be unique and follow the format: 4-20 chars, uppercase A-Z, 0-9, hyphens
- Example row:

  ```csv
  1,USB Cable A-A,USBC-1001,3.99,25,5,WireWorks
  ```

When importing, the app matches products by SKU and updates their details.

---

## Screenshots

- **Main Table:** Lists all products, with low-stock items highlighted.
- **Add/Edit Dialog:** Enter product details in a simple form.
- **Adjust Stock Dialog:** Increase or decrease stock for a selected product.
- **Low Stock View:** Shows only items needing reorder.

---

## Extending the App

This code was designed to be easy for students to understand and modify.  
Possible stretch goals:

- Add multi-location inventory (add a location column)
- Barcode field for products
- Automatic reorder suggestions (export a reorder list to CSV)

---

## License

This project is intended for educational use and classroom assignments.  
Feel free to modify and use as needed for your course.
