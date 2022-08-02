from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class PhraseTypes(Base):
    __tablename__ = 'phrase_types'
    
    id=Column(Integer, primary_key=True, autoincrement=True)
    type_name=Column(String, unique=True, nullable=False)
    description=Column(String, nullable=True)

    def __init__(self, type_name: str, description: str) -> None:
        self.type_name = type_name
        self.description = description