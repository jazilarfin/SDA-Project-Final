from extension import db


class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)
    registration_no = db.Column(db.String(20), unique=True, nullable=False)  # Vehicle registration number
    vehicle_type = db.Column(db.String(50), nullable=False)  # Type of vehicle
    capacity = db.Column(db.Integer, nullable=False)  # Capacity in kilograms
    ownership_status = db.Column(db.String(10), nullable=False)  # Ownership status (own/private)

    def __repr__(self):
        return f"<Vehicle {self.registration_no}: {self.vehicle_type}, {self.capacity}kg, {self.ownership_status}>"
    

class OwnedVehicle(Vehicle):
    __tablename__ = 'owned_vehicles'

    id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), primary_key=True)
    mileage = db.Column(db.Float, nullable=False)  # Maintenance cost for owned vehicles
    driverName = db.Column(db.String(50), nullable=False)  # Type of vehicle

    __mapper_args__ = {
        'polymorphic_identity': 'owned_vehicle',
    }

    def __repr__(self):
        return f"<OwnedVehicle {self.registration_no}: {self.vehicle_type}, {self.capacity}kg, Maintenance: ${self.maintenance_cost}>"



class RentedVehicle(Vehicle):
    __tablename__ = 'rented_vehicles'

    id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), primary_key=True)
    rental_company = db.Column(db.String(50), nullable=False)  

    rank = db.Column(db.Integer, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'rented_vehicle',
    }