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

    __mapper_args__ = {
        'polymorphic_identity': 'brand',
        'polymorphic_on': type
    }







class BrandOwned(Brand):
    __tablename__ = 'brands_owned'
    id = db.Column(db.Integer, db.ForeignKey('brands.id'), primary_key=True)
    numOfWorker = db.Column(db.Integer, nullable=False)
    extras = db.Column(db.String(50), nullable=True)
    __mapper_args__ = {
        'polymorphic_identity': 'brand_owned',
    }


class BrandOutSource(Brand):
    __tablename__ = 'brands_outsource'
    id = db.Column(db.Integer, db.ForeignKey('brands.id'), primary_key=True)
    rank = db.Column(db.Integer, nullable=False)
    special = db.Column(db.String(50), nullable=True)
    __mapper_args__ = {
        'polymorphic_identity': 'brand_outsource',
    }