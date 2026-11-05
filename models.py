from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, JSON, DateTime, func

class Base(DeclarativeBase):
    pass

class Diagram(Base):
    __tablename__ = 'diagrams'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    diagram_type = Column(String, nullable=False)
    data = Column(JSON, nullable=False)            
    settings = Column(JSON, nullable=True)         
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Diagram(id={self.id}, name='{self.name}', type='{self.diagram_type}')>"