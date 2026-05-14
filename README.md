# Riths Bistro - Food Ordering System

**CS665 - Project 3**  
**Name:** Makthala Rithika 
**WSU ID:** D652Q337

---

## Project Description

For this project I built a food ordering web application called Rith's Bistro. The idea is that restaurant staff can use this app to keep track of customers, manage the food menu, and handle orders all in one place.

The app lets you:
- Add and manage customers
- Add food items to the menu with prices and categories
- Place orders for customers with multiple items
- Update order status (Pending, Preparing, Out for Delivery, Delivered)
- See a dashboard that shows total revenue, number of orders, and the most popular items

I used this project to practice building a real full-stack application connected to an actual database.

---

## Technical Stack Requirements

- **Language:** Python 3
- **Backend:** Flask
- **Database:** SQLite using SQLAlchemy ORM
- **Frontend:** HTML5, CSS3, Bootstrap 5, Jinja2 templates
- **Version Control:** Git

---

## Installation Instructions

### Step 1 - Clone or Download the Repository
git clone https://github.com/MakthalaRithika/food_ordering_app.git
cd food_ordering_app

### Step 2 - Create a Virtual Environment

On Windows:
python -m venv venv
venv\Scripts\activate

On Mac/Linux:
python3 -m venv venv
source venv/bin/activate

### Step 3 - Install the Required Packages
pip install -r requirements.txt

---

## Database Setup

The database gets created automatically the first time while running the app. If I want to set it up manually then I can run:

mkdir instance
sqlite3 instance/food_ordering.db < schema.sql

To reset the database just delete instance/food_ordering.db and run the app again.

---

## How to Run the App

python app.py

Then open the browser and go to http://127.0.0.1:5000

To stop the app press Ctrl + C in the terminal.

---

## How to Use the App

**Dashboard** - shows a summary of all data including total revenue and top selling items.

**Customers** - add, edit, delete customers and view their order history.

**Menu** - add food items with prices and categories, mark items available or unavailable.

**Orders** - view all orders, click any order to see details and update the status.

**New Order** - pick a customer, add menu items with quantities, and submit. Everything saves in one database transaction.

## Project Structure

```
food_ordering_app/
├── app.py                  # Main Flask application (routes, models, validation)
├── requirements.txt        # Python dependencies
├── schema.sql              # Final 3NF SQL schema with seed data
├── README.md               # This file
├── NORMALIZATION.md        # Full 3NF normalization report
├── AI_LOG.md               # AI assistance disclosure log
├── .gitignore              # Excludes venv/, __pycache__/, instance/
├── static/
│   ├── css/style.css       # Custom dark-themed stylesheet
│   └── js/main.js          # Sidebar toggle and flash message logic
└── templates/
    ├── base.html           # Base layout with sidebar navigation
    ├── dashboard.html      # Summary dashboard
    ├── customers.html      # Customer list
    ├── customer_form.html  # Add/edit customer form
    ├── customer_detail.html# Customer profile and order history
    ├── menu.html           # Menu item list
    ├── menu_form.html      # Add/edit menu item form
    ├── orders.html         # Order list
    ├── order_detail.html   # Order details and status update
    └── order_form.html     # Interactive new order builder
```

---

## Key Features Explained

### Multi-Table CRUD
Full Create, Read, Update, and Delete operations are implemented across:
- `Customers` table
- `Menu_Items` table
- `Orders` and `Order_Items` tables

### Relationship Management
- **One-to-Many:** One Customer can have many Orders. Viewable on the Customer Detail page.
- **Many-to-Many:** Orders and Menu Items are linked through the `Order_Items` bridge table.

### Transaction Logic
When placing a new order, the app uses a database transaction:
1. An `Order` record is created and flushed to get the `order_id`
2. One `OrderItem` record is inserted per line item
3. Both commit together — if anything fails, `db.session.rollback()` is called and nothing is saved

### Data Validation
Server-side validation is enforced on every form:
- Name and email cannot be empty
- Email must contain `@` and must be unique
- Price must be a positive number
- Quantity must be a positive integer

### Summary Dashboard
The dashboard uses SQL aggregate functions:
- `COUNT` — total customers, total orders, pending/delivered counts
- `SUM` — total revenue across all order items
- `AVG` — average order value
- `GROUP BY` — top 3 selling menu items by quantity sold

---

