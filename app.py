from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.sql import extract
from sqlalchemy import func
import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = os.urandom(24)



app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'your_secret_key'

login_manager = LoginManager(app)
login_manager.login_view = '/'

@app.route('/register_page')
def register_page():
     return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    
    username_entered = request.form.get('username') 
    password_entered = request.form.get('password') 
    print('trying to fetch')
    if not username_entered or not password_entered:
        print('not received')           #handle not fields not entered
        return redirect(url_for('register_page'))
    else:
        if User.query.filter_by(username=username_entered).first(): 
            flash('Username already exists. Please choose a different one.', 'danger') 
            return redirect(url_for('register_page')) # Hash the password 
        new_user = User(username=username_entered)
        new_user.set_password(password_entered)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    
@app.route('/signin_button', methods=['POST'])
def signin_button():
    button_pressed=request.form['login_buttons']
    if button_pressed=="REGISTER":
        return redirect(url_for('register_page'))
    else:
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            print('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            print('Invalid email or password.')
            return render_template('index.html')


@app.route('/sidebar_buttons', methods=['POST'])
@login_required
def sidebar_buttons():
    button_pressed = request.form['button']
    if button_pressed == 'dashboard':
        return redirect(url_for('dashboard'))
    elif button_pressed == 'brand':
        return redirect(url_for('brand'))
    elif button_pressed == 'vehicle':
        return redirect(url_for('vehicle'))
    elif button_pressed == 'orders':
        return redirect(url_for('orders'))
    elif button_pressed == 'salesman':
        return redirect(url_for('salesman'))
    else:
        logout_user()
        return redirect(url_for('home'))
    

class User(db.Model,UserMixin):
    __tablename__='users'

    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String(20),nullable=False,unique=True)
    password=db.Column(db.String(30),nullable=False)

    def __repr__(self):
        return f"Username {self.username}"
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    @property
    def is_active(self):
        return True 
    


# Brand and BrickType Models
class Brand(db.Model):
    __tablename__ = 'brands'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    contact_no = db.Column(db.String(12), unique=True, nullable=False)
    principal_contact = db.Column(db.String(12), nullable=False)

    # Relationship to BrickType
    brick_types = db.relationship('BrickType', backref='brand', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Brand {self.name} - Location: {self.location}>"


class BrickType(db.Model):
    __tablename__ = 'brick_types'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_name = db.Column(db.String(50), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)  # Foreign key to Brand

    # Enforce a unique constraint on type_name and brand_id
    __table_args__ = (
        db.UniqueConstraint('type_name', 'brand_id', name='unique_brick_type_per_brand'),
    )


    def __repr__(self):
        return f"<BrickType {self.type_name} for Brand ID {self.brand_id}>"



# Order and Item Models
#class Order(db.Model):
 #   __tablename__ = 'orders'
#
 #   id = db.Column(db.Integer, primary_key=True)
  #  customer_name = db.Column(db.String(50), nullable=False)
   # contact = db.Column(db.String(15), nullable=False)  # Customer contact number
    #address = db.Column(db.String(150), nullable=False)  # Delivery address
   # totalbill = db.Column(db.Integer, nullable=False)  # Delivery address

    #vehicle_reg_number = db.Column(db.String(20), nullable=True)  # Vehicle registration number
#    vehicle_rent = db.Column(db.Float, nullable=True)  # Rent cost of the vehicle
 #   labor_cost = db.Column(db.Float, nullable=True)  # Cost of labor
  #  salesman_name = db.Column(db.String(50), nullable=True)  # Salesperson name
   # date = db.Column(db.Date, nullable=False, default=datetime.utcnow)  # Order date
   # items = db.relationship('Item', backref='order', cascade="all, delete-orphan")  # Relationship to Item

    #def __repr__(self):
     #   return f"<Order {self.id}: {self.customer_name} on {self.date}>"
#---------------------------------

#naya waal order ka data base
class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)  # Order ID
    customer_name = db.Column(db.String(100), nullable=False)  # Customer's name
    customer_contact = db.Column(db.String(15), nullable=False)  # Customer's contact number
    customer_address = db.Column(db.String(200), nullable=False)  # Customer's address
    vehicle_rent = db.Column(db.Float, nullable=False)  # Vehicle rent
    labor_cost = db.Column(db.Float, nullable=False)  # Labor cost
    total_amount = db.Column(db.Float, nullable=False)  # Total amount for the order
    order_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    # Foreign keys to the related tables
    salesman_id = db.Column(db.Integer, db.ForeignKey('salesmen.id'), nullable=False)  # Salesman ID
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)  # Vehicle ID

    # Relationships
    salesman = db.relationship('Salesman', backref=db.backref('orders', lazy=True))  # Salesman relationship
    vehicle = db.relationship('Vehicle', backref=db.backref('orders', lazy=True))  # Vehicle relationship
    items = db.relationship('Item', backref=db.backref('order', lazy=True), cascade='all, delete-orphan')  # Items relationship

    def __repr__(self):
        return f"<Order {self.id}: {self.customer_name}, {self.total_amount}, {self.order_date}>"


#--------------------------
#naya wala item table
class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)  # Item ID
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)  # Foreign key to Order table
    brick_type_name = db.Column(db.String(50), nullable=False)  # Name of the brick type
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)  # Brand ID
    quantity = db.Column(db.Integer, nullable=False)  # Quantity of the brick
    price = db.Column(db.Float, nullable=False)  # Price of the brick
    total_price = db.Column(db.Float, nullable=False)  # Total price for this item (quantity * price)

    # Relationship to Order
    #order = db.relationship('Order', backref=db.backref('items', lazy=True))

    # Relationship to Brand
    brand = db.relationship('Brand', backref=db.backref('items', lazy=True))

    def __repr__(self):
        return f"<Item {self.id}: {self.quantity} of {self.brick_type_name} for Order {self.order_id}>"




# class Item(db.Model):
#     __tablename__ = 'items'

#     id = db.Column(db.Integer, primary_key=True)
#     order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)  # Foreign key to Order
#     brick_type = db.Column(db.String(50), nullable=False)  # Type of bricks
#     brand = db.Column(db.String(50), nullable=False)  # Brand of the bricks
#     quantity = db.Column(db.Integer, nullable=False)  # Quantity of bricks
#     price = db.Column(db.Float, nullable=False)  # Price of bricks

#     def __repr__(self):
#         return f"<Item {self.id}: {self.brick_type} - {self.brand} ({self.quantity} @ {self.price})>"

# Vehicle Model
class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)
    registration_no = db.Column(db.String(20), unique=True, nullable=False)  # Vehicle registration number
    vehicle_type = db.Column(db.String(50), nullable=False)  # Type of vehicle
    capacity = db.Column(db.Integer, nullable=False)  # Capacity in kilograms
    ownership_status = db.Column(db.String(10), nullable=False)  # Ownership status (own/private)

    def __repr__(self):
        return f"<Vehicle {self.registration_no}: {self.vehicle_type}, {self.capacity}kg, {self.ownership_status}>"
    
# Salesman Model
class Salesman(db.Model):
    __tablename__ = 'salesmen'

    id = db.Column(db.Integer, primary_key=True)  # Salesman ID (Primary Key)
    name = db.Column(db.String(100), nullable=False)  # Salesman's name
    contact_no = db.Column(db.String(15), unique=True, nullable=False)  # Salesman's contact number
    cnic = db.Column(db.String(15), unique=True, nullable=False)  # Salesman's CNIC (Computerized National Identity Card)

    def __repr__(self):
        return f"<Salesman {self.name}: Contact No. {self.contact_no}, CNIC {self.cnic}>"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')




@app.route('/dashboard')
@login_required
def dashboard():
   
   recent_orders = Order.query.order_by(Order.order_date.desc()).limit(10).all()
   net_income = db.session.query(func.sum(Order.total_amount)).scalar() or 0
   sales = db.session.query(
        extract('month', Order.order_date).label('month'),
        db.func.sum(Order.total_amount).label('total_sales')
    ).group_by(
        extract('month', Order.order_date)
    ).order_by('month').all()

    
   import calendar

   labels = [calendar.month_name[int(row[0])] for row in sales]

   values = [row[1] for row in sales]  # Total sales
   return render_template("dashboard.html",net_income=net_income,recent_orders=recent_orders, labels=labels, values=values)
    #return render_template('dashboard.html')




@app.route('/order_list_buttons', methods=['POST'])
def orders_list_buttons():
    button_value = request.form.get('button')  # Get the value of the button clicked from the form
    if button_value == 'add_brand':  # If the "add_brand" button was clicked
        return redirect(url_for('add_brand'))  # Redirect to the "add_brand" route
    
    filter_type = request.form.get('filters')  # Type of filter selected
    search_text = request.form.get('search_text')  # Text input for filtering
    
    # Base query for filtering
    query = db.session.query(Order)

    # Apply filters
    if filter_type == 'name':
        query = query.filter(Order.customer_name.ilike(f'%{search_text}%'))
    elif filter_type == 'date':
       
        try:
            # Convert input text to datetime to ensure it's in the correct format
            input_date = datetime.strptime(search_text, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Order.order_date) == input_date)
        except ValueError:
            # Return an error message if the date format is incorrect
            flash("Please enter the date in YYYY-MM-DD format.")
            return redirect(url_for('orders'))
    elif filter_type == 'brick_type':
        query = query.join(Item).filter(Item.brick_type_name.ilike(f'%{search_text}%'))
    elif filter_type == 'salesman':
        query = query.join(Salesman).filter(Salesman.cnic.ilike(f'%{search_text}%'))
    elif filter_type == 'vehicle_id':
        query = query.join(Vehicle).filter(Vehicle.registration_no.ilike(f'%{search_text}%'))
    elif filter_type == 'amount':
        try:
            amount = float(search_text)
            query = query.filter(Order.total_amount == amount)
        except ValueError:
            # Handle invalid amount format
            return render_template('orders.html', error="Invalid amount format. Enter a number.")
    else:
        return render_template('orders.html', error="Invalid filter selection.")

    # Execute query
    orders = query.all()
    
    return render_template('filtered_order.html',orders=orders)
    
    

@app.route('/orders', methods=['GET'])
@login_required
def orders():
    page = request.args.get('page', 1, type=int)  # Get the current page number, default is 1
    per_page = 5  # Number of orders per page
    # orders_paginated = Order.query.paginate(page=page, per_page=per_page)

    # orders_paginated = Order.query.order_by(Order.date.desc()).paginate(page=page, per_page=per_page)
    orders_paginated = Order.query.order_by(Order.order_date.desc()).paginate(page=page, per_page=per_page)

    return render_template('orders.html', orders=orders_paginated.items, pagination=orders_paginated)



@app.route('/order/<int:order_id>', methods=['GET'])
@login_required
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order_details.html', order=order)


@app.route('/edit_order/<int:order_id>', methods=['GET'])
@login_required
def edit_order(order_id):
    order = Order.query.get(order_id)  # Fetch the order by ID
    if not order:
        flash('Order not found!', 'danger')
        return redirect(url_for('orders'))
    
    vehicles = Vehicle.query.all()  # Fetch all vehicles
    salesmen = Salesman.query.all()
    brands = Brand.query.all()
    bricks = BrickType.query.all()
    return render_template('edit_order.html', order=order, vehicles=vehicles, salesmen=salesmen, brands=brands, bricks=bricks)



#pehlay wala edit order route 

# @app.route('/edit_order/<int:order_id>', methods=['POST'])
# def edit_order_submit(order_id):
#     order = Order.query.get(order_id)
#     if not order:
#         flash('Order not found!', 'danger')
#         return redirect(url_for('orders'))

#     # Update order details
#     order.customer_name = request.form['customer_name']
#     order.contact = request.form['contact']
#     order.address = request.form['address']
#     order.vehicle_reg_number = request.form['vehicle_reg_number']
#     order.vehicle_rent = request.form['vehicle_rent']
#     order.labor_cost = request.form['labor_cost']
#     order.salesman_name = request.form['salesman_name']

#     # Update item details
#     for i, item in enumerate(order.items, start=1):
#         item.brick_type = request.form[f'brick_type_{i}']
#         item.brand = request.form[f'brand_{i}']
#         item.quantity = request.form[f'quantity_{i}']
#         item.price = request.form[f'price_{i}']

#     db.session.commit()
#     flash('Order updated successfully!', 'success')
#     return redirect(url_for('orders'))
#---------------------------

#naya wala edit order route
@app.route('/edit_order/<int:order_id>', methods=['POST'])
@login_required
def edit_order_submit(order_id):
    order = Order.query.get(order_id)
    if not order:
        print("hello")
        flash('Order not found!', 'danger')
        return redirect(url_for('orders'))

    if request.method == 'POST':
        try:
            print("in try")
            print(request.form)
            print("after form print")
            # Update order details from the form
            order.customer_name = request.form['customer_name']
            print("in try 1")

            order.customer_contact = request.form['contact']
            print("in try 2")
            order.customer_address = request.form['address']
            print("in try 3")

            order.vehicle_id = request.form['vehicle_id']  # Select vehicle ID, not registration number
            print("in try 4")
            
            order.vehicle_rent = float(request.form['vehicle_rent'])
            print("in try 5")
            
            order.labor_cost = float(request.form['labor_cost'])
            print("in try 6")
            
            order.total_amount = float(request.form['total_amount'])  # Assuming the user enters this or it's calculated
            print("in try 7")
            
            #order.order_date = datetime.strptime(request.form['order_date'], '%Y-%m-%d %H:%M:%S')  # Assuming date format
            print("in try 8")
            # Update salesman ID
            order.salesman_id = request.form['salesman_id']



            print("all updated")
            # Update item details
            # First, clear the existing items for this order
            #order.items.clear()
            print("items clear")
            # Add new items
            # Update existing items
            order.items.clear()  # Remove current items

            # Get item data from the form
            brands = request.form.getlist('brand[]')
            brick_types = request.form.getlist('brick_type[]')
            quantities = request.form.getlist('quantity[]')
            prices = request.form.getlist('price[]')

            # Add updated items back to the order
            for i in range(len(brands)):
                quantity = int(quantities[i])
                price = float(prices[i])
                total_price = quantity * price  # Calculate total price for the item

                new_item = Item(
                    order_id=order.id,
                    brand_id=int(brands[i]),
                    brick_type_name=brick_types[i],
                    quantity=quantity,
                    price=price,
                    total_price=total_price  # Set the total price
                )
                db.session.add(new_item)



            db.session.commit()
            flash('Order updated successfully!', 'success')
            return redirect(url_for('orders'))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", 'danger')
            return render_template('edit_order.html', order=order)
    
    return render_template('edit_order.html', order=order)


    # print(vehicles)  # This will output the list of vehicles to the console
 




#pehlay wala add order route

# @app.route('/add_order', methods=['GET', 'POST'])
# def add_order():
#     if request.method == 'POST':
#         try:
#             customer_name = request.form['customer_name']
#             customer_contact = request.form['customer_contact']
#             customer_address = request.form['customer_address']
#             vehicle_reg_number = request.form['vehicle_reg_number']
#             vehicle_rent = float(request.form['vehicle_rent'])
#             labor_cost = float(request.form['labor_cost'])
#             salesman_name = request.form['salesman_name']

#             new_order = Order(
#                 customer_name=customer_name,
#                 customer_contact=customer_contact,
#                 customer_address=customer_address,
#                 vehicle_reg_number=vehicle_reg_number,
#                 vehicle_rent=vehicle_rent,
#                 labor_cost=labor_cost,
#                 salesman_name=salesman_name,
#                 date=datetime.now()
#             )

#             db.session.add(new_order)
#             db.session.flush()

#             items_count = len(request.form.getlist('brick_type'))
#             for i in range(items_count):
#                 brick_type = request.form.getlist('brick_type')[i]
#                 brand = request.form.getlist('brand')[i]
#                 quantity = int(request.form.getlist('quantity')[i])
#                 price = float(request.form.getlist('price')[i])

#                 new_item = Item(
#                     order_id=new_order.id,
#                     brick_type=brick_type,
#                     brand=brand,
#                     quantity=quantity,
#                     price=price
#                 )

#                 db.session.add(new_item)

#             db.session.commit()
#             flash("Order and items added successfully!", "success")
#             return redirect(url_for('orders'))

#         except Exception as e:
#             db.session.rollback()
#             flash(f"An error occurred: {e}", "danger")
#             return render_template('add_order.html')
#     vehicles = Vehicle.query.all()
#     return render_template('add_order.html' , vehicles=vehicles)

#-------------
#naya wala add order route
@app.route('/add_order', methods=['GET', 'POST'])
@login_required
def add_order():
    if request.method == 'POST':
        try:
            # Collecting the form data from the request
            customer_name = request.form['customer_name']
            customer_contact = request.form['customer_contact']
            customer_address = request.form['customer_address']
            vehicle_id = request.form['vehicle_id']  # Use vehicle_id from the form
            salesman_id = request.form['salesman_id']  # Use vehicle_id from the form

            vehicle_rent = float(request.form['vehicle_rent'])
            labor_cost = float(request.form['labor_cost'])
            total_amount = float(request.form['total_amount'])  # Assuming total_amount is calculated
            order_date = datetime.now()  # Use current timestamp for order date

            # Retrieve the vehicle object using vehicle_id
            vehicle = Vehicle.query.get(vehicle_id)
            # if not vehicle:
            #     flash("Vehicle not found!", "danger")
            #     return redirect(url_for('add_order'))
            salesman = Salesman.query.get(salesman_id)

            
            # Retrieve the salesman ID (by name)
            # salesman = Salesman.query.filter_by(name=request.form['salesman_name']).first()
            # if not salesman:
            #     flash("Salesman not found!", "danger")
            #     return redirect(url_for('add_order'))
            #print(request.form)
            # Create a new order
            new_order = Order(
                customer_name=customer_name,
                customer_contact=customer_contact,
                customer_address=customer_address,
                vehicle_rent=vehicle_rent,
                labor_cost=labor_cost,
                total_amount=total_amount,
                order_date=order_date,
                vehicle_id=vehicle.id,  # Store the vehicle ID
                salesman_id=salesman.id  # Store the salesman ID
            )

            db.session.add(new_order)
            db.session.flush()  # Flush to get the new order's ID


            print(f"Brick Types: {request.form.getlist('brick_type_1')}")
            print(f"Brands: {request.form.getlist('brand_1')}")
            print(f"Quantities: {request.form.getlist('quantity_1')}")
            print(f"Prices: {request.form.getlist('price_1')}")


            item_index = 1  # Start with the first item
            while f'brick_type_{item_index}' in request.form:
                # Extract the data for this item
                print("in loop")
                brick_type = request.form.get(f'brick_type_{item_index}')
                print(brick_type)
                brand = request.form.get(f'brand_{item_index}')
                print(brand)
                quantity = int(request.form.get(f'quantity_{item_index}', 0))
                print(quantity)
                price = float(request.form.get(f'price_{item_index}', 0.0))
                print(price)
                total_price = quantity * price
                print("in loop 1")    

                # Create a new item and add it to the session
                new_item = Item(
                    order_id=new_order.id,
                    brick_type_name=brick_type,
                    brand_id=int(brand),
                    quantity=quantity,
                    price=price,
                    total_price=total_price
                )
                print("in loop 2")

                db.session.add(new_item)
                item_index += 1  # Move to the next item
                print("item added")

            # Commit the changes

            print("out loop")

            db.session.commit()
            print("committed")
            flash("Order and items added successfully!", "success")
            print("redirecting")
            return redirect(url_for('orders'))

        except Exception as e:
            db.session.rollback()
            print("rollbackho gaya")

            flash(f"An error occurred: {e}", "danger")
            return render_template('add_order.html')

    # Retrieve all vehicles for dropdown
    vehicles = Vehicle.query.all()
    # Retrieve all salesmen for dropdown
    salesmen = Salesman.query.all()
    # Retrieve all brands for dropdown
    brands = Brand.query.all()

    bricks = BrickType.query.all()

    return render_template('add_order.html', vehicles=vehicles, salesmen=salesmen, brands=brands, bricks=bricks)




# Route to handle button clicks for the vehicle list page
@app.route('/vehicle_list_buttons', methods=['POST'])
def vehicle_list_buttons():
    button_value = request.form.get('button')  # Get the value of the button clicked from the form
    if button_value == 'add_vehicle':  # If the "add_vehicle" button was clicked
        return redirect(url_for('add_vehicle'))  # Redirect to the "add_vehicle" route
    
    
    filters = request.form.getlist('filters')  # Get selected filters as list
    search_text = request.form.get('search_text', '')  # Get search text

    # Start with the base query
    query = Vehicle.query

    # Apply filters based on selected checkboxes
    if 'reg_no' in filters:
        query = query.filter(Vehicle.registration_no.ilike(f'%{search_text}%'))
    if 'type' in filters:
        query = query.filter(Vehicle.vehicle_type.ilike(f'%{search_text}%'))
    if 'capacity' in filters:
        query = query.filter(Vehicle.capacity.ilike(f'%{search_text}%'))
    if 'owned' in filters:
        query=query.filter(Vehicle.ownership_status.ilike(f'%own'))
    if 'private' in filters:
        query=query.filter(Vehicle.ownership_status.ilike(f'%private'))
    # Execute the query
    vehicle = query.all()


    return render_template('filtered_vehicle.html',vehicles=vehicle)

# Route to display the vehicle list page with pagination
@app.route('/vehicle', methods=['GET'])
@login_required
def vehicle():
    page = request.args.get('page', 1, type=int)  # Get the current page number from the URL query parameter
    per_page = 5  # Number of vehicles to display per page
    vehicles_paginated = Vehicle.query.paginate(page=page, per_page=per_page)  # Query the vehicles with pagination

    # Render the vehicle list template and pass the paginated vehicles and pagination data
    return render_template('vehicle.html', vehicles=vehicles_paginated.items, pagination=vehicles_paginated)

# Route to display the details of a specific vehicle
@app.route('/vehicle/<int:vehicle_id>', methods=['GET'])
@login_required
def vehicle_details(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)  # Fetch the vehicle by ID or return 404 if not found
    
    # Render the vehicle details template and pass the fetched vehicle data
    return render_template('vehicle_details.html', vehicle=vehicle)

# Route to handle adding a new vehicle (GET for form, POST for submission)
@app.route('/add_vehicle', methods=['GET', 'POST'])
@login_required
def add_vehicle():
    if request.method == 'POST':  # If the form is submitted (POST request)
        try:
            # Get form data for the new vehicle
            registration_no = request.form['vehicle_reg_number']
            vehicle_type = request.form['vehicle_type']
            capacity = int(request.form['vehicle_capacity'])  # Convert capacity to integer
            ownership_status = request.form['ownership_status']

            # Create a new Vehicle instance with the provided data
            new_vehicle = Vehicle(
                registration_no=registration_no,
                vehicle_type=vehicle_type,
                capacity=capacity,
                ownership_status=ownership_status
            )

            # Add the new vehicle to the database and commit the transaction
            db.session.add(new_vehicle)
            db.session.commit()

            flash("Vehicle added successfully!", "success")  # Flash a success message
            return redirect(url_for('vehicle'))  # Redirect to the vehicle list page

        except Exception as e:  # If there's an error while adding the vehicle
            db.session.rollback()  # Rollback the database transaction
            flash(f"Error adding vehicle: {e}", "danger")  # Flash an error message
            return render_template('add_vehicle.html')  # Return the add vehicle form with error message

    return render_template('add_vehicle.html')  # Render the form to add a vehicle (GET request)

# Route to handle editing a specific vehicle (GET for form, POST for submission)
@app.route('/edit_vehicle/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)  # Fetch the vehicle by ID or return 404 if not found

    if request.method == 'POST':  # If the form is submitted (POST request)
        try:
            # Update the vehicle details with the form data
            vehicle.registration_no = request.form['vehicle_reg_number']
            vehicle.vehicle_type = request.form['vehicle_type']
            vehicle.capacity = int(request.form['vehicle_capacity'])  # Convert capacity to integer
            vehicle.ownership_status = request.form['ownership_status']

            # Commit the changes to the database
            db.session.commit()

            flash("Vehicle updated successfully!", "success")  # Flash a success message
            return redirect(url_for('vehicle_details', vehicle_id=vehicle.id))  # Redirect to the vehicle details page

        except Exception as e:  # If there's an error while updating the vehicle
            db.session.rollback()  # Rollback the database transaction
            flash(f"Error updating vehicle: {e}", "danger")  # Flash an error message

    # Render the form to edit the vehicle with the existing data for a GET request
    return render_template('edit_vehicle.html', vehicle=vehicle)



# Route to handle button clicks for the salesman list page
@app.route('/salesman_list_buttons', methods=['POST'])
def salesman_list_buttons():
    button_value = request.form.get('button')  # Get the value of the button clicked from the form
    if button_value == 'add_salesman':  # If the "add_salesman" button was clicked
        return redirect(url_for('add_salesman'))  # Redirect to the "add_salesman" route
    
    filters = request.form.getlist('filters')  # Get selected filters as list
    search_text = request.form.get('search_text', '')  # Get search text

    # Start with the base query
    query = Salesman.query

    # Apply filters based on selected checkboxes
    if 'name' in filters:
        query = query.filter(Salesman.name.ilike(f'%{search_text}%'))
    if 'cnic' in filters:
        query = query.filter(Salesman.cnic.ilike(f'%{search_text}%'))
    if 'contact' in filters:
        query = query.filter(Salesman.contact_no.ilike(f'%{search_text}%'))

    # Execute the query
    salesmen = query.all()


    return render_template('filtered_salesman.html',salesmen=salesmen)

# Route to display the salesman list page with pagination
@app.route('/salesman', methods=['GET'])
@login_required
def salesman():
    page = request.args.get('page', 1, type=int)  # Get the current page number from the URL query parameter
    per_page = 5  # Number of salesmen to display per page
    salesmen_paginated = Salesman.query.paginate(page=page, per_page=per_page)  # Query the salesmen with pagination

    # Render the salesman list template and pass the paginated salesmen and pagination data
    return render_template('salesman.html', salesmen=salesmen_paginated.items, pagination=salesmen_paginated)

# Route to display the details of a specific salesman
@app.route('/salesman/<int:salesman_id>', methods=['GET'])
@login_required
def salesman_details(salesman_id):
    salesman = Salesman.query.get_or_404(salesman_id)  # Fetch the salesman by ID or return 404 if not found
    
    # Render the salesman details template and pass the fetched salesman data
    return render_template('salesman_details.html', salesman=salesman)

# Route to handle adding a new salesman (GET for form, POST for submission)
@app.route('/add_salesman', methods=['GET', 'POST'])
@login_required
def add_salesman():
    if request.method == 'POST':  # If the form is submitted (POST request)
        try:
            # Get form data for the new salesman
            name = request.form['salesman_name']
            contact = request.form['salesman_contact']
            cnic = request.form['salesman_cnic']

            # Create a new Salesman instance with the provided data
            new_salesman = Salesman(
                name=name,
                contact_no=contact,
                cnic=cnic
            )

            # Add the new salesman to the database and commit the transaction
            db.session.add(new_salesman)
            db.session.commit()

            flash("Salesman added successfully!", "success")  # Flash a success message
            return redirect(url_for('salesman'))  # Redirect to the salesman list page

        except Exception as e:  # If there's an error while adding the salesman
            db.session.rollback()  # Rollback the database transaction
            flash(f"Error adding salesman: {e}", "danger")  # Flash an error message
            return render_template('add_salesman.html')  # Return the add salesman form with error message

    return render_template('add_salesman.html')  # Render the form to add a salesman (GET request)

# Route to handle editing a specific salesman (GET for form, POST for submission)
@app.route('/edit_salesman/<int:salesman_id>', methods=['GET', 'POST'])
@login_required
def edit_salesman(salesman_id):
    salesman = Salesman.query.get_or_404(salesman_id)  # Fetch the salesman by ID or return 404 if not found

    if request.method == 'POST':  # If the form is submitted (POST request)
        try:
            # Update the salesman details with the form data
            salesman.name = request.form['salesman_name']
            salesman.contact_no = request.form['salesman_contact']
            salesman.cnic = request.form['salesman_cnic']

            # Commit the changes to the database
            db.session.commit()

            flash("Salesman updated successfully!", "success")  # Flash a success message
            return redirect(url_for('salesman_details', salesman_id=salesman.id))  # Redirect to the salesman details page

        except Exception as e:  # If there's an error while updating the salesman
            db.session.rollback()  # Rollback the database transaction
            flash(f"Error updating salesman: {e}", "danger")  # Flash an error message

    # Render the form to edit the salesman with the existing data for a GET request
    return render_template('edit_salesman.html', salesman=salesman)


# Route to handle button clicks for the brand list page
@app.route('/brand_list_buttons', methods=['POST'])
def brand_list_buttons():
    button_value = request.form.get('button')  # Get the value of the button clicked from the form
    if button_value == 'add_brand':  # If the "add_brand" button was clicked
        return redirect(url_for('add_brand'))  # Redirect to the "add_brand" route
    

    
    filters = request.form.getlist('filters')  # Get selected filters as list
    search_text = request.form.get('search_text', '')  # Get search text

    # Start with the base query
    query = Brand.query

    # Apply filters based on selected checkboxes
    if 'name' in filters:
        query = query.filter(Brand.name.ilike(f'%{search_text}%'))
    if 'location' in filters:
        query = query.filter(Brand.location.ilike(f'%{search_text}%'))
    if 'contact' in filters:
        query = query.filter(Brand.contact_no.ilike(f'%{search_text}%'))
    if 'p_contact' in filters:
        query=query.filter(Brand.principal_contact.ilike(f'%own'))
    
    brand = query.all()

    if 'brick_type' in filters:
        brand = Brand.query.join(BrickType).filter(
        BrickType.type_name.ilike(f'%{search_text}%')
    ).all()
    #     query=query.filter(Vehicle.ownership_status.ilike(f'%private'))
    # Execute the query
    


    return render_template('filtered_brand.html',brands=brand)
    
# Route to display the brand list page with pagination
@app.route('/brand', methods=['GET'])
@login_required
def brand():
    page = request.args.get('page', 1, type=int)  # Get the current page number from the URL query parameter
    per_page = 5  # Number of brands to display per page
    brands_paginated = Brand.query.paginate(page=page, per_page=per_page)  # Query the brands with pagination

    # Render the brand list template and pass the paginated brands and pagination data
    return render_template('brand.html', brands=brands_paginated.items, pagination=brands_paginated)

# Route to display the details of a specific brand
@app.route('/brand/<int:brand_id>', methods=['GET'])
@login_required
def brand_details(brand_id):
    brand = Brand.query.get_or_404(brand_id)  # Fetch the brand by ID or return 404 if not found
    
    # Render the brand details template and pass the fetched brand data
    return render_template('brand_details.html', brand=brand)



# Route to handle adding a new brand (GET for form, POST for submission)
@app.route('/add_brand', methods=['GET', 'POST'])
@login_required
def add_brand():
    if request.method == 'POST':  # If the form is submitted (POST request)
        try:

            print(request.form)  # Logs all submitted form data
            print(request.form.getlist('brick_types'))  # Logs brick types

            # Get form data for the new brand
            brand_name = request.form['brand_name']
            location = request.form['location']
            principal_contact = request.form['principal_contact']
            contact_no = request.form['contact_no']
            brick_types = request.form.getlist('brick_types[]')

            print(request.form.getlist('brick_types[]'))


            # Create a new Brand instance with the provided data
            new_brand = Brand(
                name=brand_name,
                location=location,
                principal_contact=principal_contact,
                contact_no=contact_no
            )

            # Add the brand to the database and commit the transaction
            db.session.add(new_brand)
            db.session.commit()

            print(f"New Brand ID: {new_brand.id}")
            print(f"Brick Types Received: {brick_types}")

            

            # Now add the brick types (if any)
            for brick_type in brick_types:
                new_brick_type = BrickType(
                    type_name=brick_type.strip(),
                    brand_id=new_brand.id  # Associate this brick type with the brand
                )
                db.session.add(new_brick_type)

            db.session.commit()

            flash("Brand and brick types added successfully!", "success")  # Flash a success message
            return redirect(url_for('brand'))  # Redirect to the brand list page

        except Exception as e:  # If there's an error while adding the brand
            db.session.rollback()  # Rollback the database transaction
            flash(f"Error adding brand: {e}", "danger")  # Flash an error message
            return render_template('add_brand.html')  # Return the add brand form with error message

    return render_template('add_brand.html')  # Render the form to add a brand (GET request)


@app.route('/edit_brand/<int:brand_id>', methods=['GET', 'POST'])
@login_required
def edit_brand(brand_id):
    # Fetch the brand details by ID
    brand = Brand.query.get(brand_id)
    if not brand:
        return "Brand not found", 404

    if request.method == 'POST':
        # Update brand details
        brand.brand_name = request.form['brand_name']
        brand.location = request.form['location']
        brand.principal_contact = request.form['principal_contact']
        brand.contact_no = request.form['contact_no']

        # Get the new list of brick types from the form
        new_brick_types = set(request.form.getlist('brick_types[]'))  # Ensure uniqueness

        # Fetch current brick types from the database
        existing_brick_types = set(brick.type_name for brick in brand.brick_types)

        # Determine which brick types to add and remove
        to_add = new_brick_types - existing_brick_types
        to_remove = existing_brick_types - new_brick_types

        # Remove old brick types
        for brick_type in to_remove:
            brick_to_remove = BrickType.query.filter_by(brand_id=brand.id, type_name=brick_type).first()
            if brick_to_remove:
                db.session.delete(brick_to_remove)

        # Add new brick types
        for brick_type in to_add:
            new_brick = BrickType(brand_id=brand.id, type_name=brick_type)
            db.session.add(new_brick)

        # Save changes to the database
        db.session.commit()

        return redirect(url_for('brand_details', brand_id=brand.id))  # Redirect to the brand details page

    # Render the edit form with pre-filled values
    return render_template('edit_brand.html', brand=brand)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)




