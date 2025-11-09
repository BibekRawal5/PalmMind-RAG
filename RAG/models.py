from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    n_chunks = Column(Integer, nullable=False, default=0)
    chunking_strategy = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    meta = Column(JSON, nullable=True)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    date = Column(String, nullable=False)  
    time = Column(String, nullable=False)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())
