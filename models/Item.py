from extension import db

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


