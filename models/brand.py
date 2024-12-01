from extension import db

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
