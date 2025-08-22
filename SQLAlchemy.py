import sqlalchemy
from sqlalchemy import Column, Integer, String, DECIMAL, Date, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key = True)
    name = Column(String(50))
    user_categories = relationship('UserCategory', back_populates= 'user' )
    incomes = relationship('Income', back_populates= 'user')
    expenses = relationship('Expense', back_populates= 'user')
    savings = relationship('Saving', back_populates= 'user')

class UserCategory(Base):
    __tablename__ = 'user_categories'
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable = False)
    user = relationship('User', back_populates= 'user_categories')
    incomes = relationship('Income', back_populates= 'category_relationship')
    expenses = relationship('Expense', back_populates= 'category_relationship')
    limit = Column(Integer, nullable = True)


class Income(Base):
    __tablename__ = 'incomes'
    id = Column(Integer, primary_key = True)
    category_id = Column(Integer, ForeignKey('user_categories.id'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    amount = Column(DECIMAL,  nullable=False)
    date = Column(Date,  nullable=False)
    is_fixed = Column(Boolean,  nullable=False)
    user = relationship('User', back_populates= 'incomes')
    category_relationship = relationship('UserCategory', back_populates= 'incomes')

class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key= True)
    category_id = Column(Integer, ForeignKey('user_categories.id'), nullable=False)
    amount = Column(DECIMAL,  nullable=False)
    date = Column(Date, nullable=False)
    is_fixed = Column(Boolean,  nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates= 'expenses')
    category_relationship = relationship('UserCategory', back_populates= 'expenses')

class Saving(Base):
    __tablename__ = 'savings'
    id = Column(Integer, primary_key= True)
    amount = Column(DECIMAL,  nullable=False)
    date = Column(Date,  nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates= 'savings')