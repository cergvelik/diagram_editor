from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Diagram(Base):
    __tablename__ = 'diagrams'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    diagram_type = Column(String, nullable=False)
    title = Column(String, default="")
    xlabel = Column(String, default="")
    ylabel = Column(String, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    data_points = relationship(
        "DiagramData",
        back_populates="diagram",
        cascade="all, delete-orphan",
        order_by="DiagramData.position"
    )


class DiagramData(Base):
    __tablename__ = 'diagram_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    diagram_id = Column(Integer, ForeignKey('diagrams.id', ondelete='CASCADE'), nullable=False)
    label = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    position = Column(Integer, nullable=False)

    diagram = relationship("Diagram", back_populates="data_points")