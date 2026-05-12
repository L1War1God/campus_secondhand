import os

class Config:
    SECRET_KEY = 'your-secret-key-change-this'
    
    # PostgreSQL 数据库连接
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456@localhost:5432/campus_secondhand'
    SQLALCHEMY_TRACK_MODIFICATIONS = False