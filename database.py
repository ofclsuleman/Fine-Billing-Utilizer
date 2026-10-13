# -*- coding: utf-8 -*-
# database.py - SQLite data layer for Fine Billing Utilizer

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "fine_billing.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS business (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT DEFAULT '',
    email TEXT DEFAULT '',
    address TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    company TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    email TEXT DEFAULT '',
    address TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    category TEXT DEFAULT '',
    price REAL,
    stock INTEGER
);
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_no TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,
    party_id INTEGER,
    party_name TEXT DEFAULT '',
    date TEXT NOT NULL,
    subtotal REAL DEFAULT 0,
    tax REAL DEFAULT 0,
    discount REAL DEFAULT 0,
    total REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    product_id INTEGER,
    product_name TEXT NOT NULL,
    price REAL NOT NULL,
    quantity REAL NOT NULL,
    total REAL NOT NULL
);
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


# ---------------- Business ----------------
def get_business():
    conn = get_conn()
    row = conn.execute("SELECT * FROM business ORDER BY id LIMIT 1").fetchone()
    conn.close()
    return row


def create_business(name):
    conn = get_conn()
    conn.execute("INSERT INTO business (name) VALUES (?)", (name.strip(),))
    conn.commit()
    conn.close()


def update_business(name):
    conn = get_conn()
    conn.execute("UPDATE business SET name=? WHERE id=(SELECT id FROM business LIMIT 1)",
                 (name.strip(),))
    conn.commit()
    conn.close()


# ---------------- Customers ----------------
def add_customer(name, phone="", email="", address=""):
    conn = get_conn()
    conn.execute("INSERT INTO customers (name, phone, email, address) VALUES (?,?,?,?)",
                 (name.strip(), phone.strip(), email.strip(), address.strip()))
    conn.commit()
    conn.close()


def update_customer(cid, name, phone="", email="", address=""):
    conn = get_conn()
    conn.execute("UPDATE customers SET name=?, phone=?, email=?, address=? WHERE id=?",
                 (name.strip(), phone.strip(), email.strip(), address.strip(), cid))
    conn.commit()
    conn.close()


def delete_customer(cid):
    conn = get_conn()
    conn.execute("DELETE FROM customers WHERE id=?", (cid,))
    conn.commit()
    conn.close()


def get_customers(search=""):
    conn = get_conn()
    if search:
        s = "%" + search.strip() + "%"
        rows = conn.execute(
            "SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? ORDER BY name",
            (s, s, s)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM customers ORDER BY name").fetchall()
    conn.close()
    return rows


def get_customer(cid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM customers WHERE id=?", (cid,)).fetchone()
    conn.close()
    return row


# ---------------- Suppliers ----------------
def add_supplier(name, company="", phone="", email="", address=""):
    conn = get_conn()
    conn.execute("INSERT INTO suppliers (name, company, phone, email, address) VALUES (?,?,?,?,?)",
                 (name.strip(), company.strip(), phone.strip(), email.strip(), address.strip()))
    conn.commit()
    conn.close()


def update_supplier(sid, name, company="", phone="", email="", address=""):
    conn = get_conn()
    conn.execute("UPDATE suppliers SET name=?, company=?, phone=?, email=?, address=? WHERE id=?",
                 (name.strip(), company.strip(), phone.strip(), email.strip(), address.strip(), sid))
    conn.commit()
    conn.close()


def delete_supplier(sid):
    conn = get_conn()
    conn.execute("DELETE FROM suppliers WHERE id=?", (sid,))
    conn.commit()
    conn.close()


def get_suppliers(search=""):
    conn = get_conn()
    if search:
        s = "%" + search.strip() + "%"
        rows = conn.execute(
            "SELECT * FROM suppliers WHERE name LIKE ? OR company LIKE ? OR phone LIKE ? ORDER BY name",
            (s, s, s)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM suppliers ORDER BY name").fetchall()
    conn.close()
    return rows


def get_supplier(sid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM suppliers WHERE id=?", (sid,)).fetchone()
    conn.close()
    return row


# ---------------- Products ----------------
def add_product(name, description="", category="", price=None, stock=None):
    conn = get_conn()
    conn.execute("INSERT INTO products (name, description, category, price, stock) VALUES (?,?,?,?,?)",
                 (name.strip(), description.strip(), category.strip(), price, stock))
    conn.commit()
    conn.close()


def update_product(pid, name, description="", category="", price=None, stock=None):
    conn = get_conn()
    conn.execute("UPDATE products SET name=?, description=?, category=?, price=?, stock=? WHERE id=?",
                 (name.strip(), description.strip(), category.strip(), price, stock, pid))
    conn.commit()
    conn.close()


def delete_product(pid):
    conn = get_conn()
    conn.execute("DELETE FROM products WHERE id=?", (pid,))
    conn.commit()
    conn.close()


def get_products(search=""):
    conn = get_conn()
    if search:
        s = "%" + search.strip() + "%"
        rows = conn.execute(
            "SELECT * FROM products WHERE name LIKE ? OR category LIKE ? ORDER BY name",
            (s, s)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM products ORDER BY name").fetchall()
    conn.close()
    return rows


def get_product(pid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    conn.close()
    return row


# ---------------- Invoices ----------------
def next_invoice_no(conn, inv_type):
    prefix = "FBU-S-" if inv_type == "sale" else "FBU-P-"
    n = conn.execute("SELECT COUNT(*) AS c FROM invoices WHERE type=?", (inv_type,)).fetchone()["c"] + 1
    return "%s%04d" % (prefix, n)


def peek_invoice_no(inv_type):
    conn = get_conn()
    no = next_invoice_no(conn, inv_type)
    conn.close()
    return no


def create_invoice(inv_type, party_id, party_name, tax, discount, items):
    # items: list of dicts with keys product_id (or None), product_name, price, quantity
    conn = get_conn()
    invoice_no = next_invoice_no(conn, inv_type)
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    subtotal = round(sum(i["price"] * i["quantity"] for i in items), 2)
    total = round(subtotal + tax - discount, 2)
    cur = conn.execute(
        "INSERT INTO invoices (invoice_no, type, party_id, party_name, date, subtotal, tax, discount, total) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (invoice_no, inv_type, party_id, party_name, date, subtotal, tax, discount, total))
    invoice_id = cur.lastrowid
    for it in items:
        line_total = round(it["price"] * it["quantity"], 2)
        conn.execute(
            "INSERT INTO invoice_items (invoice_id, product_id, product_name, price, quantity, total) "
            "VALUES (?,?,?,?,?,?)",
            (invoice_id, it.get("product_id"), it["product_name"], it["price"], it["quantity"], line_total))
        if it.get("product_id"):
            if inv_type == "sale":
                conn.execute("UPDATE products SET stock = COALESCE(stock, 0) - ? WHERE id = ?",
                             (it["quantity"], it["product_id"]))
            else:
                conn.execute("UPDATE products SET stock = COALESCE(stock, 0) + ? WHERE id = ?",
                             (it["quantity"], it["product_id"]))
    conn.commit()
    conn.close()
    return invoice_no, date, subtotal, total


def get_invoices(inv_type=None, search=""):
    conn = get_conn()
    q = "SELECT * FROM invoices WHERE 1=1"
    args = []
    if inv_type in ("sale", "purchase"):
        q += " AND type=?"
        args.append(inv_type)
    if search:
        s = "%" + search.strip() + "%"
        q += " AND (invoice_no LIKE ? OR party_name LIKE ?)"
        args += [s, s]
    q += " ORDER BY id DESC"
    rows = conn.execute(q, args).fetchall()
    conn.close()
    return rows


def get_invoice_by_no(invoice_no):
    conn = get_conn()
    row = conn.execute("SELECT * FROM invoices WHERE invoice_no=?", (invoice_no,)).fetchone()
    conn.close()
    return row


def get_invoice_items(invoice_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM invoice_items WHERE invoice_id=? ORDER BY id", (invoice_id,)).fetchall()
    conn.close()
    return rows


def party_invoices(party_name, inv_type):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM invoices WHERE party_name=? AND type=? ORDER BY id DESC",
        (party_name, inv_type)).fetchall()
    conn.close()
    return rows


# ---------------- Dashboard summary ----------------
def invoice_summary():
    conn = get_conn()

    def scalar(q):
        return conn.execute(q).fetchone()[0]

    summary = {
        "sales": scalar("SELECT COALESCE(SUM(total),0) FROM invoices WHERE type='sale'"),
        "purchases": scalar("SELECT COALESCE(SUM(total),0) FROM invoices WHERE type='purchase'"),
        "sale_count": scalar("SELECT COUNT(*) FROM invoices WHERE type='sale'"),
        "purchase_count": scalar("SELECT COUNT(*) FROM invoices WHERE type='purchase'"),
        "customer_count": scalar("SELECT COUNT(*) FROM customers"),
        "supplier_count": scalar("SELECT COUNT(*) FROM suppliers"),
        "product_count": scalar("SELECT COUNT(*) FROM products"),
        "recent": conn.execute("SELECT * FROM invoices ORDER BY id DESC LIMIT 8").fetchall(),
        "low_stock": conn.execute(
            "SELECT * FROM products WHERE stock IS NOT NULL AND stock <= 5 ORDER BY stock LIMIT 8").fetchall(),
    }
    conn.close()
    return summary
