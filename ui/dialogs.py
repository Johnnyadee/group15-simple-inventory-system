import tkinter as tk
from tkinter import simpledialog, messagebox

class AddEditProductDialog(tk.Toplevel):
	def __init__(self, parent, title, product_id=None):
		super().__init__(parent)
		self.title(title)
		self.result_ok = False
		self.product_id = product_id
		self.transient(parent)
		self.grab_set()
		self._build_ui()
		self.protocol("WM_DELETE_WINDOW", self.destroy)

	def _build_ui(self):
		import inventory.inventory as inv
		fields = [
			("Name", "name"),
			("SKU", "sku"),
			("Price", "price"),
			("Stock", "stock"),
			("Reorder Level", "reorder_level"),
			("Supplier", "supplier"),
		]
		self.vars = {}
		frame = tk.Frame(self)
		frame.pack(padx=12, pady=12)
		product = inv.get_product(self.product_id) if self.product_id else None
		for idx, (label, key) in enumerate(fields):
			tk.Label(frame, text=label).grid(row=idx, column=0, sticky="e", pady=2)
			var = tk.StringVar()
			if product:
				value = getattr(product, key, "")
				var.set(str(value) if value is not None else "")
			self.vars[key] = var
			tk.Entry(frame, textvariable=var).grid(row=idx, column=1, pady=2)

		btn_frame = tk.Frame(self)
		btn_frame.pack(pady=8)
		ok_btn = tk.Button(btn_frame, text="OK", width=10, command=self.on_ok)
		ok_btn.pack(side="left", padx=6)
		cancel_btn = tk.Button(btn_frame, text="Cancel", width=10, command=self.destroy)
		cancel_btn.pack(side="left", padx=6)

	def on_ok(self):
		import inventory.inventory as inv
		try:
			name = self.vars["name"].get().strip()
			sku = self.vars["sku"].get().strip().upper()
			price = float(self.vars["price"].get())
			stock = int(self.vars["stock"].get())
			reorder_level = int(self.vars["reorder_level"].get())
			supplier = self.vars["supplier"].get().strip() or None
			if self.product_id:
				inv.update_product(self.product_id, name=name, sku=sku, price=price, reorder_level=reorder_level, supplier=supplier)
				inv.adjust_stock(self.product_id, stock - inv.get_product(self.product_id).stock)
			else:
				inv.create_product(name, sku, price, stock, reorder_level, supplier)
			self.result_ok = True
			self.destroy()
		except Exception as e:
			messagebox.showerror("Error", str(e))

from inventory import inventory as inv

class AdjustStockDialog(tk.Toplevel):
	def __init__(self, parent, product_id, product_name):
		super().__init__(parent)
		self.title(f"Adjust Stock for {product_name}")
		self.result_ok = False
		self.product_id = product_id
		self.transient(parent)
		self.grab_set()
		self._build_ui(product_name)
		self.protocol("WM_DELETE_WINDOW", self.destroy)

	def _build_ui(self, product_name):
		label = tk.Label(self, text=f"Adjust stock for: {product_name}")
		label.pack(padx=12, pady=(12,4))
		self.delta_var = tk.StringVar()
		entry = tk.Entry(self, textvariable=self.delta_var)
		entry.pack(padx=12, pady=4)
		entry.focus_set()

		btn_frame = tk.Frame(self)
		btn_frame.pack(pady=8)
		ok_btn = tk.Button(btn_frame, text="OK", width=10, command=self.on_ok)
		ok_btn.pack(side="left", padx=6)
		cancel_btn = tk.Button(btn_frame, text="Cancel", width=10, command=self.destroy)
		cancel_btn.pack(side="left", padx=6)

	def on_ok(self):
		try:
			delta = int(self.delta_var.get())
			inv.adjust_stock(self.product_id, delta)
			self.result_ok = True
			self.destroy()
		except Exception as e:
			messagebox.showerror("Error", str(e))
