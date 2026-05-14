from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from sqlalchemy import text
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Riths Bistro-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_ordering.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ─────────────────────────────────────────
# MODELS  (3NF schema)
# ─────────────────────────────────────────

class Customer(db.Model):
    __tablename__ = 'customers'
    customer_id  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name         = db.Column(db.String(100), nullable=False)
    email        = db.Column(db.String(100), nullable=False, unique=True)
    date_created = db.Column(db.Date, default=date.today)
    orders       = db.relationship('Order', backref='customer', lazy=True,
                                   cascade='all, delete-orphan')

class Category(db.Model):
    __tablename__ = 'categories'
    category_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(50), nullable=False, unique=True)
    menu_items    = db.relationship('MenuItem', backref='category_obj', lazy=True)

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    menu_id      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_name    = db.Column(db.String(100), nullable=False)
    price        = db.Column(db.Numeric(10, 2), nullable=False)
    category_id  = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    date_created = db.Column(db.Date, default=date.today)
    available    = db.Column(db.Boolean, default=True)
    order_items  = db.relationship('OrderItem', backref='menu_item', lazy=True)

class Order(db.Model):
    __tablename__ = 'orders'
    order_id     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id  = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    order_date   = db.Column(db.Date, default=date.today)
    status       = db.Column(db.String(25), nullable=False, default='Pending')
    order_items  = db.relationship('OrderItem', backref='order', lazy=True,
                                   cascade='all, delete-orphan')

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.order_items)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    orderitem_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id     = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    menu_id      = db.Column(db.Integer, db.ForeignKey('menu_items.menu_id'), nullable=False)
    quantity     = db.Column(db.Integer, nullable=False)
    unit_price   = db.Column(db.Numeric(10, 2), nullable=False)

    @property
    def subtotal(self):
        return float(self.unit_price) * self.quantity

# ─────────────────────────────────────────
# SEED DATA
# ─────────────────────────────────────────

def seed_data():
    if Customer.query.count() > 0:
        return
    cats = {n: Category(category_name=n) for n in ['Fast Food', 'Italian', 'Drinks', 'Healthy']}
    for c in cats.values():
        db.session.add(c)
    db.session.flush()

    items = [
        MenuItem(item_name='Burger', price=5.99, category_id=cats['Fast Food'].category_id),
        MenuItem(item_name='Pizza',  price=8.99, category_id=cats['Italian'].category_id),
        MenuItem(item_name='Pasta',  price=7.50, category_id=cats['Italian'].category_id),
        MenuItem(item_name='Juice',  price=3.00, category_id=cats['Drinks'].category_id),
        MenuItem(item_name='Salad',  price=4.50, category_id=cats['Healthy'].category_id),
    ]
    for i in items:
        db.session.add(i)

    customers = [
        Customer(name='Rithika',    email='rithika@mail.com',    date_created=date(2024,1,1)),
        Customer(name='Architha',   email='archi@mail.com',       date_created=date(2024,1,2)),
        Customer(name='Shreya',     email='shreya@mail.com',      date_created=date(2024,1,3)),
        Customer(name='Prashanthi', email='prashanthi@mail.com',  date_created=date(2024,1,4)),
        Customer(name='Anju',       email='anju@mail.com',        date_created=date(2024,1,5)),
    ]
    for c in customers:
        db.session.add(c)
    db.session.commit()

# ─────────────────────────────────────────
# ROUTES — Dashboard
# ─────────────────────────────────────────

@app.route('/')
def dashboard():
    total_customers = Customer.query.count()
    total_orders    = Order.query.count()
    total_menu      = MenuItem.query.count()
    pending_orders  = Order.query.filter_by(status='Pending').count()
    delivered_orders= Order.query.filter_by(status='Delivered').count()

    # Revenue via SQL aggregate
    revenue_row = db.session.execute(
        text("SELECT COALESCE(SUM(oi.quantity * oi.unit_price),0) FROM order_items oi")
    ).fetchone()
    total_revenue = float(revenue_row[0])

    avg_order_row = db.session.execute(
        text("""
            SELECT COALESCE(AVG(order_total),0) FROM (
                SELECT SUM(oi.quantity * oi.unit_price) AS order_total
                FROM order_items oi GROUP BY oi.order_id
            )
        """)
    ).fetchone()
    avg_order = float(avg_order_row[0])

    # Top 3 menu items by quantity sold
    top_items = db.session.execute(
        text("""
            SELECT m.item_name, SUM(oi.quantity) AS total_sold
            FROM order_items oi
            JOIN menu_items m ON oi.menu_id = m.menu_id
            GROUP BY m.item_name ORDER BY total_sold DESC LIMIT 3
        """)
    ).fetchall()

    recent_orders = (Order.query
                     .order_by(Order.order_date.desc())
                     .limit(5).all())

    return render_template('dashboard.html',
        total_customers=total_customers,
        total_orders=total_orders,
        total_menu=total_menu,
        pending_orders=pending_orders,
        delivered_orders=delivered_orders,
        total_revenue=total_revenue,
        avg_order=avg_order,
        top_items=top_items,
        recent_orders=recent_orders,
    )

# ─────────────────────────────────────────
# ROUTES — Customers
# ─────────────────────────────────────────

@app.route('/customers')
def customers():
    all_customers = Customer.query.order_by(Customer.name).all()
    return render_template('customers.html', customers=all_customers)

@app.route('/customers/add', methods=['GET','POST'])
def add_customer():
    if request.method == 'POST':
        name  = request.form.get('name','').strip()
        email = request.form.get('email','').strip()
        errors = []
        if not name:
            errors.append('Name is required.')
        if not email or '@' not in email:
            errors.append('A valid email is required.')
        if Customer.query.filter_by(email=email).first():
            errors.append('Email already exists.')
        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('customer_form.html', action='Add', customer=None)
        db.session.add(Customer(name=name, email=email))
        db.session.commit()
        flash(f'Customer "{name}" added successfully!', 'success')
        return redirect(url_for('customers'))
    return render_template('customer_form.html', action='Add', customer=None)

@app.route('/customers/edit/<int:cid>', methods=['GET','POST'])
def edit_customer(cid):
    c = Customer.query.get_or_404(cid)
    if request.method == 'POST':
        name  = request.form.get('name','').strip()
        email = request.form.get('email','').strip()
        errors = []
        if not name:
            errors.append('Name is required.')
        if not email or '@' not in email:
            errors.append('A valid email is required.')
        existing = Customer.query.filter_by(email=email).first()
        if existing and existing.customer_id != cid:
            errors.append('Email already in use by another customer.')
        if errors:
            for e in errors: flash(e, 'danger')
            return render_template('customer_form.html', action='Edit', customer=c)
        c.name  = name
        c.email = email
        db.session.commit()
        flash('Customer updated.', 'success')
        return redirect(url_for('customers'))
    return render_template('customer_form.html', action='Edit', customer=c)

@app.route('/customers/delete/<int:cid>', methods=['POST'])
def delete_customer(cid):
    c = Customer.query.get_or_404(cid)
    db.session.delete(c)
    db.session.commit()
    flash(f'Customer "{c.name}" deleted.', 'success')
    return redirect(url_for('customers'))

@app.route('/customers/<int:cid>')
def customer_detail(cid):
    c = Customer.query.get_or_404(cid)
    return render_template('customer_detail.html', customer=c)

# ─────────────────────────────────────────
# ROUTES — Menu
# ─────────────────────────────────────────

@app.route('/menu')
def menu():
    items = MenuItem.query.order_by(MenuItem.item_name).all()
    categories = Category.query.order_by(Category.category_name).all()
    return render_template('menu.html', items=items, categories=categories)

@app.route('/menu/add', methods=['GET','POST'])
def add_menu_item():
    categories = Category.query.order_by(Category.category_name).all()
    if request.method == 'POST':
        name      = request.form.get('item_name','').strip()
        price_str = request.form.get('price','').strip()
        cat_id    = request.form.get('category_id','').strip()
        errors = []
        if not name:
            errors.append('Item name is required.')
        try:
            price = float(price_str)
            if price <= 0:
                errors.append('Price must be positive.')
        except ValueError:
            errors.append('Price must be a valid number.')
            price = 0
        if not cat_id:
            errors.append('Category is required.')
        if errors:
            for e in errors: flash(e, 'danger')
            return render_template('menu_form.html', action='Add', item=None, categories=categories)
        db.session.add(MenuItem(item_name=name, price=price, category_id=int(cat_id)))
        db.session.commit()
        flash(f'Menu item "{name}" added!', 'success')
        return redirect(url_for('menu'))
    return render_template('menu_form.html', action='Add', item=None, categories=categories)

@app.route('/menu/edit/<int:mid>', methods=['GET','POST'])
def edit_menu_item(mid):
    item = MenuItem.query.get_or_404(mid)
    categories = Category.query.order_by(Category.category_name).all()
    if request.method == 'POST':
        name      = request.form.get('item_name','').strip()
        price_str = request.form.get('price','').strip()
        cat_id    = request.form.get('category_id','').strip()
        available = request.form.get('available') == 'on'
        errors = []
        if not name: errors.append('Item name is required.')
        try:
            price = float(price_str)
            if price <= 0: errors.append('Price must be positive.')
        except ValueError:
            errors.append('Invalid price.'); price = 0
        if errors:
            for e in errors: flash(e, 'danger')
            return render_template('menu_form.html', action='Edit', item=item, categories=categories)
        item.item_name   = name
        item.price       = price
        item.category_id = int(cat_id)
        item.available   = available
        db.session.commit()
        flash('Menu item updated.', 'success')
        return redirect(url_for('menu'))
    return render_template('menu_form.html', action='Edit', item=item, categories=categories)

@app.route('/menu/delete/<int:mid>', methods=['POST'])
def delete_menu_item(mid):
    item = MenuItem.query.get_or_404(mid)
    if item.order_items:
        flash('Cannot delete: item is referenced in existing orders.', 'danger')
        return redirect(url_for('menu'))
    db.session.delete(item)
    db.session.commit()
    flash(f'"{item.item_name}" removed from menu.', 'success')
    return redirect(url_for('menu'))

# ─────────────────────────────────────────
# ROUTES — Orders  (includes TRANSACTION)
# ─────────────────────────────────────────

@app.route('/orders')
def orders():
    all_orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template('orders.html', orders=all_orders)

@app.route('/orders/new', methods=['GET','POST'])
def new_order():
    customers  = Customer.query.order_by(Customer.name).all()
    menu_items = MenuItem.query.filter_by(available=True).order_by(MenuItem.item_name).all()

    if request.method == 'POST':
        customer_id = request.form.get('customer_id','').strip()
        item_ids    = request.form.getlist('item_ids')
        quantities  = request.form.getlist('quantities')

        errors = []
        if not customer_id:
            errors.append('Please select a customer.')
        if not item_ids:
            errors.append('Please add at least one item to the order.')

        parsed_items = []
        for iid, qty in zip(item_ids, quantities):
            try:
                q = int(qty)
                if q <= 0: raise ValueError
            except ValueError:
                errors.append(f'Quantity must be a positive integer.')
                break
            m = MenuItem.query.get(int(iid))
            if m:
                parsed_items.append((m, q))

        if errors:
            for e in errors: flash(e, 'danger')
            return render_template('order_form.html', customers=customers, menu_items=menu_items)

        # ── TRANSACTION: create order + all order items atomically ──
        try:
            order = Order(customer_id=int(customer_id), order_date=date.today(), status='Pending')
            db.session.add(order)
            db.session.flush()   # get order_id before commit

            for m_item, qty in parsed_items:
                oi = OrderItem(
                    order_id   = order.order_id,
                    menu_id    = m_item.menu_id,
                    quantity   = qty,
                    unit_price = m_item.price,
                )
                db.session.add(oi)

            db.session.commit()
            flash(f'Order #{order.order_id} placed successfully!', 'success')
            return redirect(url_for('order_detail', oid=order.order_id))
        except Exception as ex:
            db.session.rollback()
            flash(f'Transaction failed — order not saved: {ex}', 'danger')
            return render_template('order_form.html', customers=customers, menu_items=menu_items)

    return render_template('order_form.html', customers=customers, menu_items=menu_items)

@app.route('/orders/<int:oid>')
def order_detail(oid):
    order = Order.query.get_or_404(oid)
    return render_template('order_detail.html', order=order)

@app.route('/orders/<int:oid>/status', methods=['POST'])
def update_order_status(oid):
    order  = Order.query.get_or_404(oid)
    status = request.form.get('status','').strip()
    allowed = ['Pending', 'Preparing', 'Out for Delivery', 'Delivered', 'Cancelled']
    if status not in allowed:
        flash('Invalid status.', 'danger')
        return redirect(url_for('order_detail', oid=oid))
    order.status = status
    db.session.commit()
    flash(f'Order status updated to "{status}".', 'success')
    return redirect(url_for('order_detail', oid=oid))

@app.route('/orders/delete/<int:oid>', methods=['POST'])
def delete_order(oid):
    order = Order.query.get_or_404(oid)
    db.session.delete(order)
    db.session.commit()
    flash(f'Order #{oid} deleted.', 'success')
    return redirect(url_for('orders'))

# ─────────────────────────────────────────
# API helper for live menu prices
# ─────────────────────────────────────────

@app.route('/api/menu-item/<int:mid>')
def api_menu_item(mid):
    item = MenuItem.query.get_or_404(mid)
    return jsonify({'price': float(item.price), 'name': item.item_name})

# ─────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True)
