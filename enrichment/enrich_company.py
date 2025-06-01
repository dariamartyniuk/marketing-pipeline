import os
from typing import Optional

import requests
import logging

BRANDFETCH_API_KEY = os.getenv("BRANDFETCH_API_KEY")
BRANDFETCH_URL = "https://api.brandfetch.io/v2/brands/"

def enrich_domain(domain: str) -> Optional[dict]:
    headers = {
        "Authorization": f"Bearer {BRANDFETCH_API_KEY}"
    }

    # Прибрати "www." якщо є
    domain = domain.lower().strip()
    if domain.startswith("www."):
        domain = domain[4:]

    url = f"{BRANDFETCH_URL}{domain}"
    logging.info(f"Fetching enrichment for domain: {domain}")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            logging.info(f"Received enrichment data for {domain}: {data}")

            return {
                "domain": domain,
                "name": data.get("name"),
                "description": data.get("description"),
                "industry": data.get("industry"),
                "location": data.get("location"),
                "ownership": "Public" if data.get("isPublic") else "Private"
            }
        else:
            logging.warning(f"Brandfetch returned {response.status_code} for domain {domain}: {response.text}")
            return None
    except Exception as e:
        logging.error(f"Error during enrichment for domain {domain}: {e}", exc_info=True)
        return None
