# TODO: define SQLAlchemy models
# tables for: PEP, Author, many-to-many relations that those could have
# models.py

import datetime

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

# Base class for our declarative models
Base = declarative_base()

# Association table to handle the many-to-many relationship between PEPs and Authors.
# This table links the 'peps' table and 'authors' table by their primary keys.
pep_author_association = Table(
    "pep_author_association",
    Base.metadata,
    Column("pep_number", Integer, ForeignKey("peps.number"), primary_key=True),
    Column("author_id", Integer, ForeignKey("authors.id"), primary_key=True),
)


class PEP(Base):
    """
    SQLAlchemy model for a Python Enhancement Proposal (PEP).
    """

    __tablename__ = "peps"

    # The PEP number is the natural primary key.
    number: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    title: Mapped[str] = mapped_column(String)
    discussions_to: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String(20))
    type: Mapped[str] = mapped_column(String(20))
    topic: Mapped[str] = mapped_column(String)
    created: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    python_version: Mapped[str | None] = mapped_column(String, nullable=True)
    post_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution: Mapped[str | None] = mapped_column(String, nullable=True)
    requires: Mapped[str | None] = mapped_column(String, nullable=True)
    replaces: Mapped[str | None] = mapped_column(String, nullable=True)
    superseded_by: Mapped[str | None] = mapped_column(String, nullable=True)
    url: Mapped[str] = mapped_column(String, nullable=False)

    # Define the many-to-many relationship to the Author model,
    # using the association table defined above.
    authors: Mapped[list["Author"]] = relationship(
        secondary=pep_author_association, back_populates="peps"
    )

    def __repr__(self) -> str:
        return f"<PEP(number={self.number}, title='{self.title[:30]}...')>"


class Author(Base):
    """
    SQLAlchemy model for a PEP author.
    """

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)

    # Define the reverse relationship back to the PEP model.
    peps: Mapped[list[PEP]] = relationship(
        secondary=pep_author_association, back_populates="authors"
    )

    def __repr__(self) -> str:
        return f"<Author(id={self.id}, name='{self.name}')>"


# Example of how to create the tables in a database
if __name__ == "__main__":
    from sqlalchemy import create_engine

    engine = create_engine("sqlite:///./PEPBoy.db")

    print("Creating tables...")
    Base.metadata.create_all(engine)
    print("Tables 'peps', 'authors', and 'pep_author_association' created.")
