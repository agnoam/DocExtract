from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.phrase_types_model import PhraseTypes
from models.phrase_model import Phrase

def create_connection() -> Any:
    engine = create_engine('postgresql://postgres:password@10.0.0.10:32001/postgres')

    # create a configured "Session" class
    Session = sessionmaker(bind=engine)

    # create a Session
    session = Session()
    return session


def create_tables(engine) -> None:
    # Create tables
    PhraseTypes.__table__.create(bind=engine, checkfirst=True)
    Phrase.__table__.create(bind=engine, checkfirst=True)
    print('All tables has been created (in case it was not exists)')

if __name__ == "__main__":
    try:
        session = create_connection()

        # A transaction
        try:
            # Should failed at second time
            new_type = PhraseTypes("Name", "Name of human-being")
            session.add(new_type)
            session.commit()
        except Exception as e:
            print(e)

        # A transaction
        first_phrase = Phrase("Noam", new_type.id)
        session.add(first_phrase)
        session.commit()

        # Closing the session to the db
        session.close()
    except Exception as e:
        print(e)