from extension import db
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
