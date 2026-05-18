from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import DATABASE_URL
from app.seed import seed_initial_data

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def init_db(seed_database: bool = True) -> None:
    SQLModel.metadata.create_all(engine)
    if seed_database:
        with Session(engine) as session:
            seed_initial_data(session)
