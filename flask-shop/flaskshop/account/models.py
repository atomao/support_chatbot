from functools import reduce
from operator import or_

from flask_login import UserMixin
from libgravatar import Gravatar
from sqlalchemy.ext.hybrid import hybrid_property

from flaskshop.constant import Permission
from flaskshop.database import Column, Model, db
from flaskshop.extensions import bcrypt


class User(Model, UserMixin):
    __tablename__ = "account_user"
    username = Column(db.String(80), unique=True, nullable=False, comment="user`s name")
    email = Column(db.String(80), unique=True, nullable=False)
    #: The hashed password
    _password = db.Column(db.String(255), nullable=False)
    nick_name = Column(db.String(255))
    is_active = Column(db.Boolean(), default=False)
    open_id = Column(db.String(80), index=True)
    session_key = Column(db.String(80), index=True)

    def __init__(self, username, email, password, **kwargs):
        super().__init__(username=username, email=email, password=password, **kwargs)

    def __str__(self):
        return self.username

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = bcrypt.generate_password_hash(value).decode("UTF-8")

    @property
    def avatar(self):
        return Gravatar(self.email).get_image()

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password.encode("utf-8"), value)


class UserAddress(Model):
    __tablename__ = "account_address"
    user_id = Column(db.Integer())
    province = Column(db.String(255))
    city = Column(db.String(255))
    district = Column(db.String(255))
    address = Column(db.String(255))
    contact_name = Column(db.String(255))
    contact_phone = Column(db.String(80))

    @property
    def full_address(self):
        return (
            f"{self.province}<br>{self.city}<br>{self.district}<br>"
            f"{self.address}<br>{self.contact_name}<br>{self.contact_phone}"
        )

    def user(self):
        return User.get_by_id(self.user_id)

    def __str__(self):
        return self.full_address


class Role(Model):
    __tablename__ = "account_role"
    name = Column(db.String(80), unique=True)
    permissions = Column(db.Integer(), default=Permission.LOGIN)


class UserRole(Model):
    __tablename__ = "account_user_role"
    user_id = Column(db.Integer())
    role_id = Column(db.Integer())
