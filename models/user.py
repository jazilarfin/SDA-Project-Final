from extension import db
from flask_login import  UserMixin

from werkzeug.security import generate_password_hash, check_password_hash


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