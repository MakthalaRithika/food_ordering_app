# Normalization Report - Rith's Bistro Food Ordering System

**CS665 - Project 3**  
**Student:** Makthala Rithika

---

## Overview

For this project I took my Project 2 database and normalized it to Third Normal Form (3NF). Below I have documented all the functional dependencies I found, the anomalies in the original design, the steps I took to fix them, and the final schema I used in my Flask application.

---

## Original Schema (from Project 2)

These were the four tables I started with:

```
Customers  (customer_id, name, email, date_created, metadata)
Menu       (menu_id, item_name, price, category, date_created, metadata)
Orders     (order_id, customer_id, order_date, total_amount, status, metadata)
Order_Items(orderitem_id, order_id, menu_id, quantity, price, metadata)
```

---

## 1. Original Functional Dependencies

### Customers Table
- customer_id → name, email, date_created, metadata
- email → customer_id (email is unique so it can also identify a customer)

### Menu Table
- menu_id → item_name, price, category, date_created, metadata
- category is just stored as a plain text string like "Italian" or "Fast Food"

### Orders Table
- order_id → customer_id, order_date, total_amount, status, metadata
- total_amount is calculated from the order items (this is a problem - see anomalies below)

### Order_Items Table
- orderitem_id → order_id, menu_id, quantity, price
- (order_id, menu_id) together can also identify a row

---

## 2. Anomaly Identification

I found four main problems with the original schema:

### Anomaly 1 - Update Anomaly in Menu.category
The category column in the Menu table was stored as a plain text string. So if I wanted to rename "Italian" to "Mediterranean" I would have to update every single row in the Menu table that had that category. If I missed even one row the data would be inconsistent.

**This is an update anomaly.**

### Anomaly 2 - Derived Value in Orders.total_amount
The total_amount column in the Orders table stores a value that can already be calculated by adding up all the order items. This causes three problems:

- If I change the quantity of an order item, total_amount does not update automatically
- When I first create an order before adding items, total_amount has no correct value
- If I delete all items from an order, total_amount still shows the old number

**This is an insertion, update, and deletion anomaly.**

### Anomaly 3 - Meaningless metadata Column
Every table had a metadata column that stored values like "system" or "meta". This column had no real purpose and just added noise to every table. It cannot be searched or used in any meaningful way.

**This causes insertion anomaly because every record needs a metadata value even though it means nothing.**

### Anomaly 4 - Confusing price Column in Order_Items
The price column in Order_Items had the same name as the price column in Menu but they serve different purposes. The Menu price is the current price of the item. The Order_Items price should be the price at the time the order was placed. These need to be clearly separated.

---

## 3. Decomposition Steps

### Step 1 - Extract Categories from Menu

**Before:**
```
Menu(menu_id, item_name, price, category, date_created, metadata)
```

**After:**
```
Categories(category_id, category_name)
Menu_Items(menu_id, item_name, price, category_id, date_created, available)
```

Now if a category name changes I only update one row in the Categories table.

### Step 2 - Remove total_amount from Orders

**Before:**
```
Orders(order_id, customer_id, order_date, total_amount, status, metadata)
```

**After:**
```
Orders(order_id, customer_id, order_date, status)
```

The total is now calculated dynamically using:
```sql
SELECT SUM(quantity * unit_price) FROM order_items WHERE order_id = ?
```

### Step 3 - Remove metadata from all tables

I removed the metadata column from all four tables since it served no purpose and caused unnecessary anomalies.

### Step 4 - Rename price to unit_price in Order_Items

**Before:**
```
Order_Items(orderitem_id, order_id, menu_id, quantity, price, metadata)
```

**After:**
```
Order_Items(orderitem_id, order_id, menu_id, quantity, unit_price)
```

This makes it clear that unit_price is the price captured at the time of the order, not the current menu price.

---

## 4. Final Relational Schema

This is the schema I used in my Flask application:

```
Categories(
    category_id   INTEGER PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE
)

Customers(
    customer_id  INTEGER PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    email        VARCHAR(100) NOT NULL UNIQUE,
    date_created DATE
)

Menu_Items(
    menu_id      INTEGER PRIMARY KEY,
    item_name    VARCHAR(100) NOT NULL,
    price        DECIMAL(10,2) NOT NULL,
    category_id  INTEGER NOT NULL → Categories(category_id),
    date_created DATE,
    available    BOOLEAN DEFAULT TRUE
)

Orders(
    order_id    INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL → Customers(customer_id),
    order_date  DATE,
    status      VARCHAR(25) NOT NULL
)

Order_Items(
    orderitem_id INTEGER PRIMARY KEY,
    order_id     INTEGER NOT NULL → Orders(order_id),
    menu_id      INTEGER NOT NULL → Menu_Items(menu_id),
    quantity     INTEGER NOT NULL,
    unit_price   DECIMAL(10,2) NOT NULL
)
```

### Why this is in 3NF

| Table       | 1NF | 2NF | 3NF | Reason |
|-------------|-----|-----|-----|--------|
| Categories  | Yes | Yes | Yes | Simple lookup, no dependencies |
| Customers   | Yes | Yes | Yes | All columns depend only on customer_id |
| Menu_Items  | Yes | Yes | Yes | category extracted into its own table |
| Orders      | Yes | Yes | Yes | total_amount removed, no derived data |
| Order_Items | Yes | Yes | Yes | unit_price is a snapshot, not derived |

- **1NF:** Every column has atomic values and there are no repeating groups
- **2NF:** Every non-key column depends on the full primary key, not just part of it
- **3NF:** No non-key column depends on another non-key column

