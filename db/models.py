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
    engine = create_engine("postgresql+psycopg2://marketing:marketing@marketing_db:5432/marketing_data")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def insert_or_update_company(session, enriched_data):
    domain = enriched_data.get("domain")
    company = session.query(Company).filter_by(domain=domain).first()

    if not company:
        company = Company(
            name=enriched_data.get("name"),
            domain=domain,
            description=enriched_data.get("description"),
            industry=enriched_data.get("industry"),
            hq=enriched_data.get("hq"),
            logo_url=enriched_data.get("logo"),
        )
        session.add(company)

    offer = Offer(
        filename=enriched_data.get("source_file"),
        text_excerpt=enriched_data.get("ocr_text", ""),
        company=company
    )
    session.add(offer)

    session.commit()
