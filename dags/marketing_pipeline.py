import sys
import os
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

sys.path.append("/opt/airflow/ocr")
sys.path.append("/opt/airflow/enrichment")
sys.path.append("/opt/airflow/db")

from ocr_utils import extract_text_from_image
from models import init_db, insert_or_update_company
from enrich_company import enrich_domain


MARKETING_FILES_DIR = "/opt/airflow/marketing_materials"

def run_ocr(**context):
    import logging
    from time import time

    all_texts = []
    logging.info(f"Starting OCR processing in {MARKETING_FILES_DIR}")

    files = os.listdir(MARKETING_FILES_DIR)
    logging.info(f"Found {len(files)} files")

    for i, filename in enumerate(files):
        if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".pdf")):
            continue

        filepath = os.path.join(MARKETING_FILES_DIR, filename)
        logging.info(f"[{i + 1}] Processing file: {filepath}")

        try:
            start = time()
            text = extract_text_from_image(filepath)
            duration = time() - start
            logging.info(f"[{i + 1}] Finished OCR in {duration:.2f}s: {filepath}")
            all_texts.append({"filename": filename, "text": text})
        except Exception as e:
            logging.error(f"[{i + 1}] Error during OCR of {filename}: {e}", exc_info=True)

    context['ti'].xcom_push(key="ocr_texts", value=all_texts)
    logging.info("OCR processing completed and XCom pushed.")


def extract_domains(**context):
    import re
    import logging

    texts = context['ti'].xcom_pull(task_ids="ocr_task", key="ocr_texts")
    logging.info(f"Received texts from OCR task: {texts}")

    if not texts:
        logging.warning("No OCR text found. Skipping domain extraction.")
        return

    domains = set()
    for entry in texts:
        lines = entry["text"]
        combined_text = " ".join(lines).lower()
        logging.info(f"Raw combined text: {combined_text}")

        fixed_text = combined_text.replace("www ", "www.").replace(" com", ".com")
        logging.info(f"Fixed domain-like text: {fixed_text}")

        found = re.findall(r"(?:www\.)?[\w\-]+\.(?:com|org|net|io|ai)", fixed_text)
        logging.info(f"Found domains: {found}")
        domains.update(found)

    domains = [d.lstrip("www.") for d in domains]
    context['ti'].xcom_push(key="domains", value=domains)
    logging.info(f"Extracted domains: {domains}")

def enrich_and_store(**context):
    import logging
    domains = context['ti'].xcom_pull(task_ids="extract_domains", key="domains")
    logging.info(f"Received domains for enrichment: {domains}")

    db = init_db()

    for domain in domains:
        logging.info(f"Enriching domain: {domain}")
        try:
            enriched = enrich_domain(domain)
            if enriched:
                logging.info(f"Inserting company: {enriched}")
                insert_or_update_company(db, enriched)
            else:
                logging.warning(f"No enrichment data returned for: {domain}")
        except Exception as e:
            logging.error(f"Error enriching domain {domain}: {e}", exc_info=True)

def print_companies():
    import sqlite3
    conn = sqlite3.connect("/opt/airflow/db/companies.db")
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM companies").fetchall()
    print("\n[DEBUG] Existing Companies in DB:")
    for row in rows:
        print(row)
    conn.close()

default_args = {
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
}

with DAG(
    dag_id="marketing_material_ingestion",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    ocr_task = PythonOperator(
        task_id="ocr_task",
        python_callable=run_ocr,
        provide_context=True,
    )

    domain_extraction = PythonOperator(
        task_id="extract_domains",
        python_callable=extract_domains,
        provide_context=True,
    )

    enrich_store = PythonOperator(
        task_id="enrich_and_store",
        python_callable=enrich_and_store,
        provide_context=True,
    )

    print_db_task = PythonOperator(
        task_id='print_companies',
        python_callable=print_companies,
        dag=dag,
    )

    ocr_task >> domain_extraction >> enrich_store >> print_db_task
