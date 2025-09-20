import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from inventory import inventory as inv
from ui.dialogs import AddEditProductDialog, AdjustStockDialog

class InventoryApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simple Inventory")

        self._build_menu()
        self._build_toolbar()
        self._build_table()
        self._build_status()

        self.refresh_table()

    def run(self):
        self.root.mainloop()

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open CSV...", command=self.on_open_csv)
        filemenu.add_command(label="Save", command=self.on_save)
        filemenu.add_command(label="Save As...", command=self.on_save_as)
        filemenu.add_separator()
        filemenu.add_command(label="Import CSV (merge)...", command=self.on_import_csv)
        filemenu.add_command(label="Export CSV...", command=self.on_export_csv)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

    def _build_toolbar(self):
        bar = ttk.Frame(self.root, padding=(8,4))
        bar.pack(side="top", fill="x")

        ttk.Button(bar, text="Add", command=self.on_add).pack(side="left", padx=4)
        ttk.Button(bar, text="Edit", command=self.on_edit).pack(side="left", padx=4)
        ttk.Button(bar, text="Adjust Stock", command=self.on_adjust).pack(side="left", padx=4)
        ttk.Button(bar, text="Delete", command=self.on_delete).pack(side="left", padx=4)

        self.btn_show_low = ttk.Button(bar, text="Show Low Stock", command=self.on_show_low)
        self.btn_show_low.pack(side="left", padx=12)

        self.path_label = ttk.Label(bar, text=f"File: {inv.current_path()}")
        self.path_label.pack(side="right")

    def _build_table(self):
        columns = ("name", "sku", "supplier", "price", "stock", "reorder")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=16)
        self.tree.heading("name", text="Name")
        self.tree.heading("sku", text="SKU")
        self.tree.heading("supplier", text="Supplier")
        self.tree.heading("price", text="Price")
        self.tree.heading("stock", text="Stock")
        self.tree.heading("reorder", text="Reorder")

        self.tree.column("name", width=200)
        self.tree.column("sku", width=120)
        self.tree.column("supplier", width=160)
        self.tree.column("price", width=80, anchor="e")
        self.tree.column("stock", width=70, anchor="e")
        self.tree.column("reorder", width=80, anchor="e")

        self.tree.tag_configure("low", background="#fff3cd")
        self.tree.tag_configure("verylow", background="#f8d7da")

        self.tree.pack(side="top", fill="both", expand=True, padx=8, pady=(0,8))
        self.tree.bind("<Double-1>", lambda e: self.on_edit())

    def _build_status(self):
        status = ttk.Frame(self.root, padding=8)
        status.pack(side="bottom", fill="x")
        self.low_label = ttk.Label(status, text="Low stock: 0", foreground="#b26b00")
        self.low_label.pack(side="left")

    def refresh_table(self, low_only: bool = False):
        for row in self.tree.get_children():
            self.tree.delete(row)
        products = inv.list_low_stock() if low_only else inv.list_products()
        low_count = len(inv.list_low_stock())

        for p in products:
            tags = ("verylow",) if p.is_low_stock and p.stock == 0 else ("low",) if p.is_low_stock else ()
            self.tree.insert(
                "",
                "end",
                iid=str(p.id),
                values=(p.name, p.sku, p.supplier or "-", f"{p.price:.2f}", p.stock, p.reorder_level),
                tags=tags,
            )
        self.low_label.config(text=f"Low stock: {low_count}")
        self.path_label.config(text=f"File: {inv.current_path()}")

    def get_selected_product_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        try:
            return int(sel[0])
        except Exception:
            return None

    def on_add(self):
        dlg = AddEditProductDialog(self.root, "Add Product", product_id=None)
        self.root.wait_window(dlg)
        if dlg.result_ok:
            self.refresh_table()

    def on_edit(self):
        pid = self.get_selected_product_id()
        if pid is None:
            messagebox.showinfo("Select a product", "Please select a product to edit.")
            return
        dlg = AddEditProductDialog(self.root, "Edit Product", product_id=pid)
        self.root.wait_window(dlg)
        if dlg.result_ok:
            self.refresh_table()

    def on_adjust(self):
        pid = self.get_selected_product_id()
        if pid is None:
            messagebox.showinfo("Select a product", "Please select a product to adjust.")
            return
        p = inv.get_product(pid)
        if not p:
            messagebox.showerror("Error", "Product not found")
            return
        dlg = AdjustStockDialog(self.root, product_id=pid, product_name=p.name)
        self.root.wait_window(dlg)
        if dlg.result_ok:
            self.refresh_table()

    def on_delete(self):
        pid = self.get_selected_product_id()
        if pid is None:
            messagebox.showinfo("Select a product", "Please select a product to delete.")
            return
        p = inv.get_product(pid)
        if not p:
            messagebox.showerror("Error", "Product not found")
            return
        if messagebox.askyesno("Delete", f'Delete "{p.name}"?'):
            inv.delete_product(pid)
            self.refresh_table()

    def on_show_low(self):
        if self.btn_show_low.cget("text") == "Show Low Stock":
            self.refresh_table(low_only=True)
            self.btn_show_low.config(text="Show All")
        else:
            self.refresh_table(low_only=False)
            self.btn_show_low.config(text="Show Low Stock")

    def on_save(self):
        try:
            inv.save_to()
            messagebox.showinfo("Saved", f"Saved to {inv.current_path()}")
        except Exception as e:
            messagebox.showerror("Save failed", str(e))

    def on_save_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Save As")
        if not path:
            return
        try:
            inv.export_csv(path)
            inv.set_current_path(path)
            messagebox.showinfo("Saved", f"Saved to {path}")
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Save failed", str(e))

    def on_open_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")], title="Open CSV")
        if not path:
            return
        try:
            inv.load_from(path)
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Open failed", str(e))

    def on_export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Export CSV")
        if not path:
            return
        try:
            inv.export_csv(path)
            messagebox.showinfo("Export complete", f"Exported to {path}")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

    def on_import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")], title="Import CSV (merge)")
        if not path:
            return
        count = inv.import_csv(path)
        messagebox.showinfo("Import complete", f"Imported {count} rows")
        self.refresh_table()