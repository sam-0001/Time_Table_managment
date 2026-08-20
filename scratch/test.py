import uuid
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))

engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

u = User()
print("Before add/flush:", u.id)
session.add(u)
print("After add, before flush:", u.id)
session.flush()
print("After flush:", u.id)
