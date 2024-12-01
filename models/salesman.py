from extension import db
class Salesman(db.Model):
    __tablename__ = 'salesmen'

    id = db.Column(db.Integer, primary_key=True)  # Salesman ID (Primary Key)
    name = db.Column(db.String(100), nullable=False)  # Salesman's name
    contact_no = db.Column(db.String(15), unique=True, nullable=False)  # Salesman's contact number
    cnic = db.Column(db.String(15), unique=True, nullable=False)  # Salesman's CNIC (Computerized National Identity Card)

    def __repr__(self):
        return f"<Salesman {self.name}: Contact No. {self.contact_no}, CNIC {self.cnic}>"