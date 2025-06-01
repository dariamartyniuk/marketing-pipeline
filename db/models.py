from sqlalchemy import Column, String, Integer, ForeignKey, Text, create_engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    domain = Column(String, unique=True, index=True)
    description = Column(Text)
    industry = Column(String)
    hq = Column(String)
    logo_url = Column(String)

    offers = relationship("Offer", back_populates="company")

class Offer(Base):
    __tablename__ = 'offers'

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    text_excerpt = Column(Text)
    company_id = Column(Integer, ForeignKey('companies.id'))

    company = relationship("Company", back_populates="offers")

def init_db():
    import sqlite3
    conn = sqlite3.connect("/opt/airflow/db/companies.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT UNIQUE,
            name TEXT,
            description TEXT,
            industry TEXT,
            location TEXT,
            ownership TEXT
        );
    """)
    return conn


def insert_or_update_company(db, company_data):
    existing = db.execute(
        "SELECT * FROM companies WHERE domain = ?", (company_data["domain"],)
    ).fetchone()

    if existing:
        db.execute(
            """UPDATE companies
               SET name = ?, description = ?, industry = ?, location = ?, ownership = ?
               WHERE domain = ?""",
            (
                company_data["name"],
                company_data["description"],
                company_data["industry"],
                company_data["location"],
                company_data["ownership"],
                company_data["domain"],
            ),
        )
    else:
        db.execute(
            """INSERT INTO companies (domain, name, description, industry, location, ownership)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                company_data["domain"],
                company_data["name"],
                company_data["description"],
                company_data["industry"],
                company_data["location"],
                company_data["ownership"],
            ),
        )

    db.commit()

