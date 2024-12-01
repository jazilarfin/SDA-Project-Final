from extension import db
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
