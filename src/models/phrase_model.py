from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class Phrase(Base):
    __tablename__ = 'phrases'
    id=Column(Integer, primary_key=True, autoincrement=True)
    phrase=Column(String, nullable=False)
    type=Column(Integer, ForeignKey("phrase_types.id"))

    def __init__(self, phrase: str, type: int) -> None:
        self.phrase = phrase
        self.type = type
