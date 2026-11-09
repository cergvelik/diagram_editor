from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_CONFIG
from models import Base, Diagram, DiagramData
import urllib.parse


def get_database_url():
    encoded_password = urllib.parse.quote_plus(DATABASE_CONFIG["password"])
    return (
        f"{DATABASE_CONFIG['drivername']}://{DATABASE_CONFIG['username']}:"
        f"{encoded_password}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/"
        f"{DATABASE_CONFIG['database']}"
    )


DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()


# CRUD
def create_diagram(name, diagram_type, labels, values, title="", xlabel="", ylabel=""):
    session = get_session()
    try:
        diagram = Diagram(
            name=name, diagram_type=diagram_type,
            title=title, xlabel=xlabel, ylabel=ylabel
        )
        for i, (lb, vl) in enumerate(zip(labels, values)):
            diagram.data_points.append(DiagramData(label=lb, value=vl, position=i))
        session.add(diagram)
        session.commit()
        session.refresh(diagram)
        return diagram
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_all_diagrams():
    session = get_session()
    try:
        return session.query(Diagram).order_by(Diagram.created_at.desc()).all()
    finally:
        session.close()


def get_diagram_by_id(diagram_id):
    session = get_session()
    try:
        return session.query(Diagram).filter_by(id=diagram_id).first()
    finally:
        session.close()


def get_diagram_data(diagram_id):
    session = get_session()
    try:
        points = (
            session.query(DiagramData)
            .filter_by(diagram_id=diagram_id)
            .order_by(DiagramData.position)
            .all()
        )
        return [p.label for p in points], [p.value for p in points]
    finally:
        session.close()


def update_diagram(diagram_id, name, diagram_type, labels, values, title="", xlabel="", ylabel=""):
    session = get_session()
    try:
        diagram = session.query(Diagram).filter_by(id=diagram_id).first()
        if not diagram:
            return None
        diagram.name = name
        diagram.diagram_type = diagram_type
        diagram.title = title
        diagram.xlabel = xlabel
        diagram.ylabel = ylabel

        session.query(DiagramData).filter_by(diagram_id=diagram_id).delete()
        for i, (lb, vl) in enumerate(zip(labels, values)):
            session.add(DiagramData(diagram_id=diagram_id, label=lb, value=vl, position=i))

        session.commit()
        return diagram
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def delete_diagram(diagram_id):
    session = get_session()
    try:
        diagram = session.query(Diagram).filter_by(id=diagram_id).first()
        if diagram:
            session.delete(diagram)
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()