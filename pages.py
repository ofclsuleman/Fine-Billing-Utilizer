# -*- coding: utf-8 -*-
# pages.py - all application pages for Fine Billing Utilizer

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

import customtkinter as ctk

import database as db

FONT = "Segoe UI"
APP_NAME = "Fine Billing Utilizer"
COMPANY = "Fine Tech's Fine Group Of Companies"
DEVELOPER = "M.Suleman Raghib"
CONTACT = "ofclsuleman@gmail.com"


def money(v):
    return "%0.2f" % v


def parse_float(text, default=None):
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


# ----------------------------------------------------------------------
# Reusable styled widgets
# ----------------------------------------------------------------------
def Card(parent, theme, **kw):
    kw.setdefault("corner_radius", 14)
    return ctk.CTkFrame(parent, fg_color=theme["card"], border_width=1,
                        border_color=theme["border"], **kw)


def Title(parent, theme, text, size=22):
    return ctk.CTkLabel(parent, text=text, font=(FONT, size, "bold"),
                        text_color=theme["text"], anchor="w")


def Entry(parent, theme, **kw):
    kw.setdefault("height", 38)
    kw.setdefault("font", (FONT, 13))
    kw.setdefault("fg_color", theme["entry"])
    kw.setdefault("text_color", theme["text"])
    kw.setdefault("border_color", theme["border"])
    return ctk.CTkEntry(parent, **kw)


def Button(parent, theme, text, command, kind="primary", **kw):
    colors = {
        "primary": (theme["accent"], theme["accent_hover"]),
        "danger": (theme["danger"], "#b13838"),
        "ghost": (theme["entry"], theme["border"]),
    }
    fg, hover = colors[kind]
    kw.setdefault("height", 38)
    kw.setdefault("font", (FONT, 13, "bold"))
    kw.setdefault("corner_radius", 8)
    if kind == "ghost":
        kw.setdefault("text_color", theme["text"])
    else:
        kw.setdefault("text_color", "#ffffff")
    return ctk.CTkButton(parent, text=text, command=command, fg_color=fg,
                         hover_color=hover, **kw)


def Option(parent, theme, values, command=None, **kw):
    kw.setdefault("font", (FONT, 13))
    kw.setdefault("fg_color", theme["entry"])
    kw.setdefault("text_color", theme["text"])
    kw.setdefault("button_color", theme["accent"])
    kw.setdefault("button_hover_color", theme["accent_hover"])
    kw.setdefault("dropdown_fg_color", theme["card"])
    kw.setdefault("dropdown_text_color", theme["text"])
    kw.setdefault("dropdown_hover_color", theme["accent"])
    kw.setdefault("height", 38)
    kw.setdefault("corner_radius", 8)
    return ctk.CTkOptionMenu(parent, values=values, command=command, **kw)


def make_tree(parent, theme, columns, widths):
    wrap = ctk.CTkFrame(parent, fg_color=theme["card"], corner_radius=12,
                        border_width=1, border_color=theme["border"])
    tree = ttk.Treeview(wrap, columns=columns, show="headings", selectmode="browse")
    for col, wd in zip(columns, widths):
        tree.heading(col, text=col)
        tree.column(col, width=wd, anchor="w", stretch=True)
    vsb = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
    vsb.pack(side="right", fill="y", pady=10, padx=(0, 10))
    return wrap, tree


# ----------------------------------------------------------------------
# Dashboard
# ----------------------------------------------------------------------
class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, theme, app=None):
        super().__init__(parent, fg_color="transparent")
        self.theme = theme
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(3, weight=1)

        biz = db.get_business()
        Title(self, theme, "👋  Welcome, %s" % (biz["name"] if biz else ""),
              24).grid(row=0, column=0, sticky="w", pady=(0, 2))
        ctk.CTkLabel(self, text="Here is your business at a glance",
                     font=(FONT, 13), text_color=theme["subtext"],
                     anchor="w").grid(row=1, column=0, columnspan=2,
                                      sticky="w", pady=(0, 14))

        s = db.invoice_summary()
        cards = [
            ("💰", money(s["sales"]), "Total Sales"),
            ("🛒", money(s["purchases"]), "Total Purchases"),
            ("🧾", str(s["sale_count"] + s["purchase_count"]), "Total Invoices"),
            ("👥", str(s["customer_count"]), "Customers"),
            ("🏭", str(s["supplier_count"]), "Suppliers"),
            ("📦", str(s["product_count"]), "Products"),
        ]
        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        for i in range(3):
            grid_frame.grid_columnconfigure(i, weight=1, uniform="card")
        for idx, (icon, value, label) in enumerate(cards):
            card = Card(grid_frame, theme)
            ctk.CTkLabel(card, text=icon, font=(FONT, 28)).pack(anchor="w",
                        padx=16, pady=(14, 0))
            ctk.CTkLabel(card, text=value, font=(FONT, 22, "bold"),
                         text_color=theme["text"]).pack(anchor="w", padx=16)
            ctk.CTkLabel(card, text=label, font=(FONT, 12),
                         text_color=theme["subtext"]).pack(anchor="w", padx=16,
                         pady=(0, 14))
            card.grid(row=idx // 3, column=idx % 3, padx=5, pady=5, sticky="ew")

        # Recent invoices
        recent_card = Card(self, theme)
        recent_card.grid(row=3, column=0, sticky="nsew", padx=(0, 6), pady=(12, 0))
        ctk.CTkLabel(recent_card, text="🕒  Recent Invoices",
                     font=(FONT, 16, "bold"),
                     text_color=theme["text"], anchor="w").pack(anchor="w",
                     padx=16, pady=(14, 6))
        wrap, self.recent_tree = make_tree(recent_card, theme,
            ("Invoice No", "Type", "Party", "Date", "Total"),
            (110, 80, 170, 140, 100))
        wrap.pack(fill="both", expand=True, padx=10, pady=(0, 12))
        if s["recent"]:
            for r in s["recent"]:
                self.recent_tree.insert("", "end", values=(
                    r["invoice_no"], r["type"].upper(), r["party_name"],
                    r["date"], money(r["total"])))
        else:
            self.recent_tree.insert("", "end", values=("—", "No invoices yet",
                                                       "", "", ""))

        # Low stock alerts
        stock_card = Card(self, theme)
        stock_card.grid(row=3, column=1, sticky="nsew", padx=(6, 0), pady=(12, 0))
        ctk.CTkLabel(stock_card, text="⚠️  Low Stock Alerts",
                     font=(FONT, 16, "bold"),
                     text_color=theme["text"], anchor="w").pack(anchor="w",
                     padx=16, pady=(14, 6))
        if s["low_stock"]:
            for p in s["low_stock"]:
                ctk.CTkLabel(stock_card,
                             text="• %s — only %s left" % (p["name"], p["stock"]),
                             font=(FONT, 13), text_color=theme["warn"],
                             anchor="w").pack(anchor="w", padx=18, pady=3)
        else:
            ctk.CTkLabel(stock_card, text="✅  Stock levels are healthy",
                         font=(FONT, 13), text_color=theme["subtext"],
                         anchor="w").pack(anchor="w", padx=18, pady=6)


# ----------------------------------------------------------------------
# Generic party page (Customers / Suppliers share the same logic)
# ----------------------------------------------------------------------
class PartyPage(ctk.CTkFrame):
    HEADING = "Parties"
    HISTORY_TYPE = "sale"
    HISTORY_LABEL = "Sales"
    FIELDS = [("name", "Name *"), ("phone", "Phone"),
              ("email", "Email"), ("address", "Address")]
    TREE_COLS = ("ID", "Name", "Phone", "Email", "Address")
    TREE_WIDTHS = (40, 150, 100, 150, 170)
    TREE_VALUES = lambda self, r: (r["id"], r["name"], r["phone"],
                                   r["email"], r["address"])

    def __init__(self, parent, theme, app=None):
        super().__init__(parent, fg_color="transparent")
        self.theme = theme
        self.selected_id = None
        self.entries = {}

        self.grid_columnconfigure(0, weight=3, uniform="p")
        self.grid_columnconfigure(1, weight=5, uniform="p")
        self.grid_rowconfigure(1, weight=1)

        Title(self, theme, self.HEADING, 24).grid(row=0, column=0,
              columnspan=2, sticky="w", pady=(0, 12))

        # --- form card ---
        form = Card(self, theme)
        form.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(form, text="Details", font=(FONT, 16, "bold"),
                     text_color=theme["text"], anchor="w").grid(
                     row=0, column=0, sticky="w", padx=18, pady=(16, 8))
        for i, (key, label) in enumerate(self.FIELDS):
            box = ctk.CTkFrame(form, fg_color="transparent")
            box.grid(row=i + 1, column=0, sticky="ew", padx=18, pady=4)
            ctk.CTkLabel(box, text=label, font=(FONT, 12),
                         text_color=theme["subtext"], anchor="w").pack(anchor="w")
            e = Entry(box, theme, placeholder_text=label)
            e.pack(fill="x", pady=(2, 0))
            self.entries[key] = e

        btns = ctk.CTkFrame(form, fg_color="transparent")
        btns.grid(row=len(self.FIELDS) + 1, column=0, sticky="ew",
                  padx=18, pady=(16, 6))
        Button(btns, theme, "➕ Add", self.add).pack(side="left", padx=(0, 6))
        Button(btns, theme, "✏️ Update", self.update, kind="ghost").pack(
            side="left", padx=6)
        Button(btns, theme, "🗑 Delete", self.delete, kind="danger").pack(
            side="left", padx=6)
        Button(btns, theme, "Clear", self.clear_form, kind="ghost").pack(
            side="left", padx=6)
        Button(form, theme, "📜  %s History" % self.HISTORY_LABEL,
               self.history, kind="ghost").grid(
               row=len(self.FIELDS) + 2, column=0, sticky="ew",
               padx=18, pady=(4, 16))

        # --- list card ---
        lst = Card(self, theme)
        lst.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        lst.grid_rowconfigure(1, weight=1)
        lst.grid_columnconfigure(0, weight=1)
        self.search_entry = Entry(lst, theme,
                                  placeholder_text="🔍  Search...", height=34)
        self.search_entry.grid(row=0, column=0, sticky="ew",
                               padx=14, pady=(14, 8))
        self.search_entry.bind("<KeyRelease>", lambda e: self.reload(
            self.search_entry.get()))
        wrap, self.tree = make_tree(lst, theme, self.TREE_COLS, self.TREE_WIDTHS)
        wrap.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 14))
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.reload()

    # --- database hooks (implemented by subclasses) ---
    def db_all(self, search):
        raise NotImplementedError

    def db_add(self, **kw):
        raise NotImplementedError

    def db_update(self, pid, **kw):
        raise NotImplementedError

    def db_delete(self, pid):
        raise NotImplementedError

    def db_get(self, pid):
        raise NotImplementedError

    # --- behaviour ---
    def reload(self, search=""):
        self.tree.delete(*self.tree.get_children())
        for r in self.db_all(search):
            self.tree.insert("", "end", iid=str(r["id"]),
                             values=self.TREE_VALUES(r))

    def on_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        row = self.db_get(int(sel[0]))
        if not row:
            return
        self.selected_id = row["id"]
        for key in self.entries:
            self.entries[key].delete(0, "end")
            self.entries[key].insert(0, row[key] or "")

    def clear_form(self):
        self.selected_id = None
        for e in self.entries.values():
            e.delete(0, "end")
        self.tree.selection_remove(self.tree.selection())

    def _form_data(self):
        return {k: e.get().strip() for k, e in self.entries.items()}

    def add(self):
        data = self._form_data()
        if not data.get("name"):
            messagebox.showwarning("Required", "Name is required.")
            return
        self.db_add(**data)
        self.reload(self.search_entry.get())
        self.clear_form()

    def update(self):
        if not self.selected_id:
            messagebox.showwarning("Select", "Select a record from the list first.")
            return
        data = self._form_data()
        if not data.get("name"):
            messagebox.showwarning("Required", "Name is required.")
            return
        self.db_update(self.selected_id, **data)
        self.reload(self.search_entry.get())
        self.clear_form()

    def delete(self):
        if not self.selected_id:
            messagebox.showwarning("Select", "Select a record from the list first.")
            return
        if not messagebox.askyesno("Delete", "Delete this record permanently?"):
            return
        self.db_delete(self.selected_id)
        self.reload(self.search_entry.get())
        self.clear_form()

    def history(self):
        if not self.selected_id:
            messagebox.showwarning("Select", "Select a record from the list first.")
            return
        row = self.db_get(self.selected_id)
        invoices = db.party_invoices(row["name"], self.HISTORY_TYPE)
        t = self.theme
        win = ctk.CTkToplevel(self)
        win.title("%s history — %s" % (self.HISTORY_LABEL, row["name"]))
        win.geometry("640x460")
        win.transient(self.winfo_toplevel())
        Title(win, t, "📜  %s — %s history" % (row["name"], self.HISTORY_LABEL),
              18).pack(anchor="w", padx=16, pady=(14, 8))
        wrap, tree = make_tree(win, t,
            ("Invoice No", "Date", "Items Total"), (140, 160, 120))
        wrap.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        total = 0
        for inv in invoices:
            tree.insert("", "end", values=(inv["invoice_no"], inv["date"],
                                           money(inv["total"])))
            total += inv["total"]
        ctk.CTkLabel(win, text="Total: %s" % money(total),
                     font=(FONT, 15, "bold"),
                     text_color=t["accent"]).pack(anchor="e", padx=18, pady=(0, 14))


class CustomersPage(PartyPage):
    HEADING = "👥  Customers"
    HISTORY_TYPE = "sale"
    HISTORY_LABEL = "Sales"

    def db_all(self, search):
        return db.get_customers(search)

    def db_add(self, **kw):
        db.add_customer(kw["name"], kw.get("phone", ""), kw.get("email", ""),
                        kw.get("address", ""))

    def db_update(self, pid, **kw):
        db.update_customer(pid, kw["name"], kw.get("phone", ""),
                           kw.get("email", ""), kw.get("address", ""))

    def db_delete(self, pid):
        db.delete_customer(pid)

    def db_get(self, pid):
        return db.get_customer(pid)


class SuppliersPage(PartyPage):
    HEADING = "🏭  Suppliers"
    HISTORY_TYPE = "purchase"
    HISTORY_LABEL = "Purchase"
    FIELDS = [("name", "Name *"), ("company", "Company"),
              ("phone", "Phone"), ("email", "Email"), ("address", "Address")]
    TREE_COLS = ("ID", "Name", "Company", "Phone", "Email")
    TREE_WIDTHS = (40, 140, 140, 100, 150)

    def TREE_VALUES(self, r):
        return (r["id"], r["name"], r["company"], r["phone"], r["email"])

    def db_all(self, search):
        return db.get_suppliers(search)

    def db_add(self, **kw):
        db.add_supplier(kw["name"], kw.get("company", ""), kw.get("phone", ""),
                        kw.get("email", ""), kw.get("address", ""))

    def db_update(self, pid, **kw):
        db.update_supplier(pid, kw["name"], kw.get("company", ""),
                           kw.get("phone", ""), kw.get("email", ""),
                           kw.get("address", ""))

    def db_delete(self, pid):
        db.delete_supplier(pid)

    def db_get(self, pid):
        return db.get_supplier(pid)


# ----------------------------------------------------------------------
# Products
# ----------------------------------------------------------------------
class ProductsPage(ctk.CTkFrame):
    def __init__(self, parent, theme, app=None):
        super().__init__(parent, fg_color="transparent")
        self.theme = theme
        self.selected_id = None
        self.entries = {}

        self.grid_columnconfigure(0, weight=3, uniform="p")
        self.grid_columnconfigure(1, weight=5, uniform="p")
        self.grid_rowconfigure(1, weight=1)

        Title(self, theme, "📦  Products", 24).grid(row=0, column=0,
              columnspan=2, sticky="w", pady=(0, 12))

        # form
        form = Card(self, theme)
        form.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(form, text="Product Details", font=(FONT, 16, "bold"),
                     text_color=theme["text"], anchor="w").grid(
                     row=0, column=0, sticky="w", padx=18, pady=(16, 8))
        fields = [("name", "Product Name *"), ("description", "Description"),
                  ("category", "Category")]
        for i, (key, label) in enumerate(fields):
            box = ctk.CTkFrame(form, fg_color="transparent")
            box.grid(row=i + 1, column=0, sticky="ew", padx=18, pady=4)
            ctk.CTkLabel(box, text=label, font=(FONT, 12),
                         text_color=theme["subtext"], anchor="w").pack(anchor="w")
            e = Entry(box, theme, placeholder_text=label)
            e.pack(fill="x", pady=(2, 0))
            self.entries[key] = e
        # optional price & stock
        for i, (key, label) in enumerate([("price", "Price (optional)"),
                                          ("stock", "Stock / Qty (optional)")]):
            box = ctk.CTkFrame(form, fg_color="transparent")
            box.grid(row=len(fields) + 1 + i, column=0, sticky="ew",
                     padx=18, pady=4)
            ctk.CTkLabel(box, text=label, font=(FONT, 12),
                         text_color=theme["subtext"], anchor="w").pack(anchor="w")
            e = Entry(box, theme, placeholder_text=label)
            e.pack(fill="x", pady=(2, 0))
            self.entries[key] = e

        btns = ctk.CTkFrame(form, fg_color="transparent")
        btns.grid(row=7, column=0, sticky="ew", padx=18, pady=(16, 16))
        Button(btns, theme, "➕ Add", self.add).pack(side="left", padx=(0, 6))
        Button(btns, theme, "✏️ Update", self.update, kind="ghost").pack(
            side="left", padx=6)
        Button(btns, theme, "🗑 Delete", self.delete, kind="danger").pack(
            side="left", padx=6)
        Button(btns, theme, "Clear", self.clear_form, kind="ghost").pack(
            side="left", padx=6)

        # list
        lst = Card(self, theme)
        lst.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        lst.grid_rowconfigure(1, weight=1)
        lst.grid_columnconfigure(0, weight=1)
        self.search_entry = Entry(lst, theme,
                                  placeholder_text="🔍  Search products...",
                                  height=34)
        self.search_entry.grid(row=0, column=0, sticky="ew",
                               padx=14, pady=(14, 8))
        self.search_entry.bind("<KeyRelease>", lambda e: self.reload(
            self.search_entry.get()))
        wrap, self.tree = make_tree(lst, theme,
            ("ID", "Name", "Category", "Price", "Stock", "Description"),
            (40, 150, 100, 80, 70, 170))
        wrap.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 14))
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.reload()

    def reload(self, search=""):
        self.tree.delete(*self.tree.get_children())
        for p in db.get_products(search):
            price = "-" if p["price"] is None else money(p["price"])
            stock = "-" if p["stock"] is None else str(p["stock"])
            self.tree.insert("", "end", iid=str(p["id"]),
                             values=(p["id"], p["name"], p["category"],
                                     price, stock, p["description"]))

    def on_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        p = db.get_product(int(sel[0]))
        if not p:
            return
        self.selected_id = p["id"]
        for key in self.entries:
            self.entries[key].delete(0, "end")
            val = p[key]
            self.entries[key].insert(0, "" if val is None else str(val))

    def clear_form(self):
        self.selected_id = None
        for e in self.entries.values():
            e.delete(0, "end")
        self.tree.selection_remove(self.tree.selection())

    def _data(self):
        d = {k: e.get().strip() for k, e in self.entries.items()}
        d["price"] = parse_float(d["price"])      # None when empty (optional)
        s = parse_float(d["stock"])
        d["stock"] = None if s is None else int(s)
        return d

    def add(self):
        d = self._data()
        if not d["name"]:
            messagebox.showwarning("Required", "Product name is required.")
            return
        db.add_product(d["name"], d["description"], d["category"],
                       d["price"], d["stock"])
        self.reload(self.search_entry.get())
        self.clear_form()

    def update(self):
        if not self.selected_id:
            messagebox.showwarning("Select", "Select a product from the list first.")
            return
        d = self._data()
        if not d["name"]:
            messagebox.showwarning("Required", "Product name is required.")
            return
        db.update_product(self.selected_id, d["name"], d["description"],
                          d["category"], d["price"], d["stock"])
        self.reload(self.search_entry.get())
        self.clear_form()

    def delete(self):
        if not self.selected_id:
            messagebox.showwarning("Select", "Select a product from the list first.")
            return
        if not messagebox.askyesno("Delete", "Delete this product permanently?"):
            return
        db.delete_product(self.selected_id)
        self.reload(self.search_entry.get())
        self.clear_form()


# ----------------------------------------------------------------------
# Invoice (sales & purchase share this page)
# ----------------------------------------------------------------------
class InvoicePage(ctk.CTkFrame):
    def __init__(self, parent, theme, inv_type, app=None):
        super().__init__(parent, fg_color="transparent")
        self.theme = theme
        self.inv_type = inv_type
        self.is_sale = inv_type == "sale"
        self.items = []
        self.last_invoice = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        heading = "🧾  New Sales Invoice" if self.is_sale else "🛒  New Purchase Invoice"
        Title(self, theme, heading, 24).grid(row=0, column=0, sticky="w")
        self.meta = ctk.CTkLabel(self, text="", font=(FONT, 13),
                                 text_color=theme["subtext"], anchor="e")
        self.meta.grid(row=0, column=0, sticky="e", pady=(0, 10))

        # ---- top card: party + item entry ----
        top = Card(self, theme)
        top.grid(row=1, column=0, sticky="ew", pady=(2, 10))
        for c, wgt in ((0, 2), (1, 2), (2, 1), (3, 1)):
            top.grid_columnconfigure(c, weight=wgt)

        party_label = "Customer *" if self.is_sale else "Supplier *"
        ctk.CTkLabel(top, text=party_label, font=(FONT, 12),
                     text_color=theme["subtext"], anchor="w").grid(
                     row=0, column=0, sticky="w", padx=(16, 8), pady=(12, 0))
        ctk.CTkLabel(top, text="Product *", font=(FONT, 12),
                     text_color=theme["subtext"], anchor="w").grid(
                     row=0, column=1, sticky="w", padx=8, pady=(12, 0))
        ctk.CTkLabel(top, text="Price", font=(FONT, 12),
                     text_color=theme["subtext"], anchor="w").grid(
                     row=0, column=2, sticky="w", padx=8, pady=(12, 0))
        ctk.CTkLabel(top, text="Quantity *", font=(FONT, 12),
                     text_color=theme["subtext"], anchor="w").grid(
                     row=0, column=3, sticky="w", padx=8, pady=(12, 0))

        self.party_menu = Option(top, theme, ["— none —"])
        self.party_menu.grid(row=1, column=0, sticky="ew", padx=(16, 8), pady=(2, 12))
        self.product_menu = Option(top, theme, ["— none —"], command=self.on_product)
        self.product_menu.grid(row=1, column=1, sticky="ew", padx=8, pady=(2, 12))
        self.e_price = Entry(top, theme, placeholder_text="0.00")
        self.e_price.grid(row=1, column=2, sticky="ew", padx=8, pady=(2, 12))
        self.e_qty = Entry(top, theme, placeholder_text="Qty")
        self.e_qty.grid(row=1, column=3, sticky="ew", padx=8, pady=(2, 12))
        Button(top, theme, "➕ Add Item", self.add_item).grid(
            row=1, column=4, padx=(8, 16), pady=(2, 12))

        # ---- middle card: items list ----
        mid = Card(self, theme)
        mid.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        mid.grid_rowconfigure(0, weight=1)
        mid.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(mid, text="Invoice Items", font=(FONT, 16, "bold"),
                     text_color=theme["text"], anchor="w").grid(
                     row=0, column=0, sticky="nw", padx=16, pady=(14, 0))
        wrap, self.tree = make_tree(mid, theme,
            ("Product", "Price", "Quantity", "Total"), (260, 110, 110, 120))
        wrap.grid(row=0, column=0, sticky="nsew", padx=10, pady=(46, 12))
        Button(mid, theme, "Remove Item", self.remove_item, kind="danger").place(
            x=140, y=16)

        # ---- bottom card: totals & actions ----
        bottom = Card(self, theme)
        bottom.grid(row=3, column=0, sticky="ew")
        for c in range(6):
            bottom.grid_columnconfigure(c, weight=1)

        ctk.CTkLabel(bottom, text="Subtotal", font=(FONT, 13),
                     text_color=theme["subtext"]).grid(row=0, column=0,
                     sticky="e", padx=8, pady=(14, 4))
        self.lbl_sub = ctk.CTkLabel(bottom, text="0.00", font=(FONT, 14, "bold"),
                                    text_color=theme["text"])
        self.lbl_sub.grid(row=1, column=0, sticky="e", padx=8, pady=(0, 14))

        ctk.CTkLabel(bottom, text="Tax", font=(FONT, 13),
                     text_color=theme["subtext"]).grid(row=0, column=1,
                     sticky="e", padx=8, pady=(14, 4))
        self.e_tax = Entry(bottom, theme, placeholder_text="0", width=90)
        self.e_tax.grid(row=1, column=1, sticky="e", padx=8, pady=(0, 14))
        self.e_tax.bind("<KeyRelease>", lambda e: self.recompute())

        ctk.CTkLabel(bottom, text="Discount", font=(FONT, 13),
                     text_color=theme["subtext"]).grid(row=0, column=2,
                     sticky="e", padx=8, pady=(14, 4))
        self.e_disc = Entry(bottom, theme, placeholder_text="0", width=90)
        self.e_disc.grid(row=1, column=2, sticky="e", padx=8, pady=(0, 14))
        self.e_disc.bind("<KeyRelease>", lambda e: self.recompute())

        ctk.CTkLabel(bottom, text="GRAND TOTAL", font=(FONT, 14, "bold"),
                     text_color=theme["accent"]).grid(row=0, column=3,
                     sticky="e", padx=8, pady=(14, 4))
        self.lbl_total = ctk.CTkLabel(bottom, text="0.00",
                                      font=(FONT, 20, "bold"),
                                      text_color=theme["accent"])
        self.lbl_total.grid(row=1, column=3, sticky="e", padx=8, pady=(0, 14))

        Button(bottom, theme, "💾  Save Invoice", self.save).grid(
            row=0, column=4, rowspan=2, padx=6, pady=12, sticky="ew")
        Button(bottom, theme, "🧹  New / Clear", self.new_invoice, kind="ghost").grid(
            row=0, column=5, rowspan=2, padx=(6, 16), pady=12, sticky="ew")

        self.reload_parties()
        self.reload_products()
        self.update_meta()

    # ---- data loading ----
    def reload_parties(self):
        rows = db.get_customers() if self.is_sale else db.get_suppliers()
        self.party_map = {}
        values = []
        for r in rows:
            disp = r["name"] + (" — " + r["phone"] if r["phone"] else "")
            if disp in self.party_map:
                disp = "%s (#%s)" % (disp, r["id"])
            self.party_map[disp] = (r["id"], r["name"])
            values.append(disp)
        if not values:
            values = ["— none —"]
        self.party_menu.configure(values=values)
        self.party_menu.set(values[0])

    def reload_products(self):
        self.product_map = {}
        values = []
        for p in db.get_products():
            disp = p["name"]
            if p["stock"] is not None:
                disp = "%s  (stock: %s)" % (disp, p["stock"])
            if disp in self.product_map:
                disp = "%s (#%s)" % (disp, p["id"])
            self.product_map[disp] = p
            values.append(disp)
        if not values:
            values = ["— none —"]
        self.product_menu.configure(values=values)
        self.product_menu.set(values[0])
        self.on_product(values[0])

    def on_product(self, disp):
        p = self.product_map.get(disp)
        self.e_price.delete(0, "end")
        if p is not None and p["price"] is not None:
            self.e_price.insert(0, str(p["price"]))

    def update_meta(self):
        no = db.peek_invoice_no(self.inv_type)
        now = datetime.now().strftime("%d %b %Y  %H:%M")
        self.meta.configure(text="Invoice No: %s    |    Date: %s" % (no, now))

    # ---- items ----
    def add_item(self):
        disp = self.product_menu.get()
        p = self.product_map.get(disp)
        if p is None:
            messagebox.showwarning("Product", "Please select a product first.")
            return
        price = parse_float(self.e_price.get(), 0.0)
        qty = parse_float(self.e_qty.get())
        if qty is None or qty <= 0:
            messagebox.showwarning("Quantity", "Enter a valid quantity greater than 0.")
            return
        self.items.append({"product_id": p["id"], "product_name": p["name"],
                           "price": round(price, 2), "quantity": qty})
        self.refresh_items()
        self.e_qty.delete(0, "end")

    def remove_item(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])
        if 0 <= idx < len(self.items):
            del self.items[idx]
        self.refresh_items()

    def refresh_items(self):
        self.tree.delete(*self.tree.get_children())
        for it in self.items:
            self.tree.insert("", "end", values=(
                it["product_name"], money(it["price"]),
                ("%g" % it["quantity"]), money(it["price"] * it["quantity"])))
        self.recompute()

    def recompute(self):
        subtotal = round(sum(i["price"] * i["quantity"] for i in self.items), 2)
        tax = parse_float(self.e_tax.get(), 0.0) or 0.0
        discount = parse_float(self.e_disc.get(), 0.0) or 0.0
        total = round(subtotal + tax - discount, 2)
        self.lbl_sub.configure(text=money(subtotal))
        self.lbl_total.configure(text=money(total))

    def new_invoice(self):
        self.items = []
        self.e_tax.delete(0, "end")
        self.e_disc.delete(0, "end")
        self.e_qty.delete(0, "end")
        self.refresh_items()

    # ---- save & export ----
    def save(self):
        if not self.items:
            messagebox.showwarning("Empty", "Add at least one item to the invoice.")
            return
        party = self.party_map.get(self.party_menu.get())
        if not party:
            messagebox.showwarning("Party", "Please select a %s first." %
                                   ("customer" if self.is_sale else "supplier"))
            return
        subtotal = round(sum(i["price"] * i["quantity"] for i in self.items), 2)
        tax = parse_float(self.e_tax.get(), 0.0) or 0.0
        discount = parse_float(self.e_disc.get(), 0.0) or 0.0
        total = round(subtotal + tax - discount, 2)
        kind = "SALES" if self.is_sale else "PURCHASE"
        if not messagebox.askyesno("Confirm",
                "Save %s invoice for %s?\n\nGrand Total: %s" %
                (kind, party[1], money(total))):
            return
        invoice_no, date, _, _ = db.create_invoice(
            self.inv_type, party[0], party[1], tax, discount, self.items)
        snapshot_items = []
        for it in self.items:
            line = dict(it)
            line["total"] = round(it["price"] * it["quantity"], 2)
            snapshot_items.append(line)
        self.last_invoice = {"invoice_no": invoice_no, "type": self.inv_type,
                             "party_name": party[1], "date": date,
                             "subtotal": subtotal, "tax": tax,
                             "discount": discount, "total": total}
        self.items = []
        self.e_tax.delete(0, "end")
        self.e_disc.delete(0, "end")
        self.refresh_items()
        self.reload_products()
        self.update_meta()
        messagebox.showinfo("Saved ✅", "Invoice %s saved successfully!" % invoice_no)
        if messagebox.askyesno("Export", "Export this invoice to a text file?"):
            self.export_last()

    def export_last(self):
        if not self.last_invoice:
            messagebox.showwarning("Export", "No invoice saved yet in this session.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=self.last_invoice["invoice_no"] + ".txt",
            filetypes=[("Text file", "*.txt")],
            title="Export invoice")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.build_invoice_text(self.last_invoice,
                                                self._last_items()))
            messagebox.showinfo("Exported ✅", "Invoice saved to:\n%s" % path)
        except OSError as e:
            messagebox.showerror("Error", "Could not export invoice:\n%s" % e)

    def _last_items(self):
        # items are cleared after save, so rebuild from the invoice in DB
        inv = db.get_invoice_by_no(self.last_invoice["invoice_no"])
        return db.get_invoice_items(inv["id"]) if inv else []

    def build_invoice_text(self, inv, items):
        kind = "SALE" if inv["type"] == "sale" else "PURCHASE"
        party_word = "Customer" if inv["type"] == "sale" else "Supplier"
        lines = []
        lines.append(APP_NAME.upper())
        lines.append(COMPANY)
        lines.append("=" * 50)
        lines.append("Invoice No : %s" % inv["invoice_no"])
        lines.append("Type       : %s" % kind)
        lines.append("%s : %s" % (party_word.ljust(10), inv["party_name"]))
        lines.append("Date       : %s" % inv["date"])
        lines.append("=" * 50)
        lines.append("%-26s%8s%7s%11s" % ("ITEM", "PRICE", "QTY", "TOTAL"))
        lines.append("-" * 50)
        for it in items:
            lines.append("%-26s%8.2f%7.2f%11.2f" % (
                it["product_name"][:26], it["price"], it["quantity"], it["total"]))
        lines.append("=" * 50)
        lines.append("Subtotal   : %s" % money(inv["subtotal"]))
        lines.append("Tax        : %s" % money(inv["tax"]))
        lines.append("Discount   : %s" % money(inv["discount"]))
        lines.append("GRAND TOTAL: %s" % money(inv["total"]))
        lines.append("=" * 50)
        lines.append("Thank you for your business!")
        lines.append("Developed by %s - %s" % (DEVELOPER, CONTACT))
        return "\n".join(lines)


# ----------------------------------------------------------------------
# Records
# ----------------------------------------------------------------------
class RecordsPage(ctk.CTkFrame):
    def __init__(self, parent, theme, app=None):
        super().__init__(parent, fg_color="transparent")
        self.theme = theme
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        Title(self, theme, "📚  Sales & Purchase Records", 24).grid(
            row=0, column=0, sticky="w", pady=(0, 12))

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.filter_menu = Option(bar, theme, ["All", "Sales", "Purchases"],
                                  command=lambda v: self.reload())
        self.filter_menu.pack(side="left")
        self.search_entry = Entry(bar, theme,
                                  placeholder_text="🔍  Search by invoice no or party...",
                                  width=320, height=38)
        self.search_entry.pack(side="left", padx=10)
        self.search_entry.bind("<KeyRelease>", lambda e: self.reload())

        card = Card(self, theme)
        card.grid(row=2, column=0, sticky="nsew")
        card.grid_rowconfigure(0, weight=1)
        card.grid_columnconfigure(0, weight=1)
        wrap, self.tree = make_tree(card, theme,
            ("Invoice No", "Type", "Party", "Date", "Subtotal", "Tax",
             "Discount", "Total"),
            (110, 80, 170, 140, 90, 70, 80, 100))
        wrap.grid(row=0, column=0, sticky="nsew", padx=10, pady=12)
        self.tree.bind("<Double-1>", lambda e: self.detail())
        ctk.CTkLabel(self, text="Tip: double-click an invoice to view its items",
                     font=(FONT, 12),
                     text_color=theme["subtext"]).grid(row=3, column=0,
                     sticky="w", pady=(8, 0))
        self.reload()

    def reload(self, *_):
        mapping = {"All": None, "Sales": "sale", "Purchases": "purchase"}
        rows = db.get_invoices(mapping[self.filter_menu.get()],
                               self.search_entry.get())
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", values=(
                r["invoice_no"], r["type"].upper(), r["party_name"], r["date"],
                money(r["subtotal"]), money(r["tax"]), money(r["discount"]),
                money(r["total"])))

    def detail(self):
        sel = self.tree.selection()
        if not sel:
            return
        invoice_no = self.tree.item(sel[0], "values")[0]
        inv = db.get_invoice_by_no(invoice_no)
        if not inv:
            return
        items = db.get_invoice_items(inv["id"])
        t = self.theme
        win = ctk.CTkToplevel(self)
        win.title("Invoice %s" % invoice_no)
        win.geometry("660x540")
        win.transient(self.winfo_toplevel())
        Title(win, t, "🧾  Invoice %s" % invoice_no, 18).pack(anchor="w",
              padx=16, pady=(14, 4))
        ctk.CTkLabel(win, text="%s  |  %s  |  %s" % (
            inv["type"].upper(), inv["party_name"], inv["date"]),
            font=(FONT, 13), text_color=t["subtext"], anchor="w").pack(
            anchor="w", padx=16, pady=(0, 8))
        wrap, tree = make_tree(win, t, ("Product", "Price", "Qty", "Total"),
                               (250, 100, 80, 110))
        wrap.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        for it in items:
            tree.insert("", "end", values=(it["product_name"],
                                           money(it["price"]),
                                           ("%g" % it["quantity"]),
                                           money(it["total"])))
        totals = ("Subtotal: %s    Tax: %s    Discount: %s    TOTAL: %s" % (
            money(inv["subtotal"]), money(inv["tax"]),
            money(inv["discount"]), money(inv["total"])))
        ctk.CTkLabel(win, text=totals, font=(FONT, 14, "bold"),
                     text_color=t["accent"], anchor="e").pack(anchor="e",
                     padx=18, pady=(0, 14))


# ----------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------
class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, theme, app=None):
        super().__init__(parent, fg_color="transparent")
        self.theme = theme
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        Title(self, theme, "⚙️  Settings", 24).grid(row=0, column=0,
              sticky="w", pady=(0, 12))

        # business
        biz_card = Card(self, theme)
        biz_card.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        ctk.CTkLabel(biz_card, text="🏢  Business", font=(FONT, 16, "bold"),
                     text_color=theme["text"], anchor="w").grid(
                     row=0, column=0, sticky="w", padx=18, pady=(14, 8))
        biz = db.get_business()
        self.e_biz = Entry(biz_card, theme, width=360)
        self.e_biz.insert(0, biz["name"] if biz else "")
        self.e_biz.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 16))
        Button(biz_card, theme, "💾  Save Business Name", self.save_business).grid(
            row=1, column=1, sticky="w", padx=(10, 18), pady=(0, 16))

        # appearance
        app_card = Card(self, theme)
        app_card.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        ctk.CTkLabel(app_card, text="🎨  Appearance", font=(FONT, 16, "bold"),
                     text_color=theme["text"], anchor="w").pack(anchor="w",
                     padx=18, pady=(14, 8))
        current = "Dark" if (app and app.mode == "dark") else "Light"
        seg = ctk.CTkSegmentedButton(app_card, values=["Light", "Dark"],
                                     command=self._theme_changed,
                                     font=(FONT, 13))
        seg.set(current)
        seg.pack(anchor="w", padx=18, pady=(0, 16))

        # about
        about = Card(self, theme)
        about.grid(row=3, column=0, sticky="ew")
        ctk.CTkLabel(about, text="ℹ️  About", font=(FONT, 16, "bold"),
                     text_color=theme["text"], anchor="w").pack(anchor="w",
                     padx=18, pady=(14, 8))
        info = ("%s\n%s\nVersion %s\n\nDeveloped by: %s\nContact: %s" % (
            APP_NAME, COMPANY, "1.0.0", DEVELOPER, CONTACT))
        ctk.CTkLabel(about, text=info, font=(FONT, 13),
                     text_color=theme["subtext"], anchor="w",
                     justify="left").pack(anchor="w", padx=18, pady=(0, 16))

    def save_business(self):
        name = self.e_biz.get().strip()
        if not name:
            messagebox.showwarning("Required", "Business name cannot be empty.")
            return
        if db.get_business():
            db.update_business(name)
        else:
            db.create_business(name)
        messagebox.showinfo("Saved ✅", "Business name updated.")
        if self.app:
            self.app._build()  # refresh sidebar title

    def _theme_changed(self, value):
        if self.app and value.lower() != self.app.mode:
            self.app.toggle_theme()
