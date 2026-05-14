-- ══════════════════════════════════════════
-- Riths Bistro Food Ordering System
-- ══════════════════════════════════════════

-- Drop existing tables (child → parent order)
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS menu_items;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS customers;

-- ── CATEGORIES (extracted from original Menu.category) ──
CREATE TABLE categories (
    category_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name VARCHAR(50) NOT NULL UNIQUE
);

-- ── CUSTOMERS ──
CREATE TABLE customers (
    customer_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    name         VARCHAR(100) NOT NULL,
    email        VARCHAR(100) NOT NULL UNIQUE,
    date_created DATE DEFAULT (DATE('now'))
);

-- ── MENU ITEMS ──
CREATE TABLE menu_items (
    menu_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name    VARCHAR(100) NOT NULL,
    price        DECIMAL(10,2) NOT NULL CHECK(price > 0),
    category_id  INTEGER NOT NULL REFERENCES categories(category_id),
    date_created DATE DEFAULT (DATE('now')),
    available    BOOLEAN DEFAULT 1
);

-- ── ORDERS (total_amount removed — derived from order_items) ──
CREATE TABLE orders (
    order_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    order_date  DATE DEFAULT (DATE('now')),
    status      VARCHAR(25) NOT NULL DEFAULT 'Pending'
        CHECK(status IN ('Pending','Preparing','Out for Delivery','Delivered','Cancelled'))
);

-- ── ORDER ITEMS ──
CREATE TABLE order_items (
    orderitem_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id     INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    menu_id      INTEGER NOT NULL REFERENCES menu_items(menu_id),
    quantity     INTEGER NOT NULL CHECK(quantity > 0),
    unit_price   DECIMAL(10,2) NOT NULL CHECK(unit_price > 0)
);

-- ── SEED DATA ──
INSERT INTO categories (category_name) VALUES
    ('Fast Food'), ('Italian'), ('Drinks'), ('Healthy');

INSERT INTO customers (name, email, date_created) VALUES
    ('Rithika',    'rithika@mail.com',    '2024-01-01'),
    ('Architha',   'archi@mail.com',      '2024-01-02'),
    ('Shreya',     'shreya@mail.com',     '2024-01-03'),
    ('Prashanthi', 'prashanthi@mail.com', '2024-01-04'),
    ('Anju',       'anju@mail.com',       '2024-01-05');

INSERT INTO menu_items (item_name, price, category_id, date_created) VALUES
    ('Burger', 5.99, 1, '2024-01-01'),
    ('Pizza',  8.99, 2, '2024-01-01'),
    ('Pasta',  7.50, 2, '2024-01-01'),
    ('Juice',  3.00, 3, '2024-01-01'),
    ('Salad',  4.50, 4, '2024-01-01');

INSERT INTO orders (customer_id, order_date, status) VALUES
    (1, '2024-02-01', 'Pending'),
    (2, '2024-02-02', 'Delivered'),
    (3, '2024-02-03', 'Pending'),
    (4, '2024-02-04', 'Delivered'),
    (5, '2024-02-05', 'Pending');

INSERT INTO order_items (order_id, menu_id, quantity, unit_price) VALUES
    (1, 1, 2, 5.99),
    (2, 2, 2, 8.99),
    (3, 3, 1, 7.50),
    (4, 4, 3, 3.00),
    (5, 5, 2, 4.50);

-- ── USEFUL VIEWS ──

-- Order totals (replaces the stored total_amount column)
CREATE VIEW order_totals AS
    SELECT o.order_id,
           o.customer_id,
           o.order_date,
           o.status,
           COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_amount
    FROM orders o
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.order_id;

-- Dashboard summary
CREATE VIEW dashboard_summary AS
    SELECT
        (SELECT COUNT(*) FROM customers)                              AS total_customers,
        (SELECT COUNT(*) FROM orders)                                 AS total_orders,
        (SELECT COUNT(*) FROM orders WHERE status = 'Pending')        AS pending_orders,
        (SELECT COUNT(*) FROM orders WHERE status = 'Delivered')      AS delivered_orders,
        (SELECT COALESCE(SUM(quantity * unit_price),0) FROM order_items) AS total_revenue;
