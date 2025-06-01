def is_new_company(db, domain):
    return not db.query(Company).filter_by(domain=domain).first()

def deduplicate_and_insert(db, company_data):
    if is_new_company(db, company_data['domain']):
        db.add(Company(**company_data))
    else:
        # Update offers for existing company
        company = db.query(Company).filter_by(domain=company_data['domain']).first()
        company.offers.append(company_data['offer'])
    db.commit()
