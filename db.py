from pydantic import EmailStr
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

Session = sessionmaker(bind=engine)
Base = declarative_base()

class ItemModel(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(
        String,
        unique=True,
        nullable=False
    )
    price = Column(Float)
    author = Column(String)
    available = Column(Boolean)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("UserModel", back_populates="items")

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(
        String,
        unique=True,
        nullable=False
    )
    email = Column(
        String,
        unique=True,
        nullable=False
    )
    password = Column(
        String,
        nullable=False
    )
    items = relationship("ItemModel", back_populates="owner")



