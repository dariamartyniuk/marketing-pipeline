# 📄 Marketing Material Ingestion Pipeline

An Airflow-based pipeline that processes marketing materials to extract company information.

---

## 🚀 Features

- **OCR with EasyOCR**: Reads text from images (JPG, PNG, PDF).
- **Domain Extraction**: Parses domains like `example.com` from the OCR’d text.
- **Company Enrichment**: Uses mock enrichment logic to simulate data retrieval.
- **Deduplication**: Prevents duplicate companies; updates existing records if reprocessed.
- **Database**: Saves data in a dedicated SQLite database (separate from Airflow metadata).

---

## 🏁 How to Run

1. **Start Airflow**
    ```bash
    docker compose up --build
    ```

2. **Add Files**
    Place your marketing materials (images) in the `./marketing_materials/` directory.

3. **Trigger DAG**
    Open [http://localhost:8080](http://localhost:8080) and run the `marketing_material_ingestion` DAG.

---
## 🏁 Results

<img width="1122" alt="Screenshot 2025-06-01 at 20 46 33" src="https://github.com/user-attachments/assets/05e15438-a170-4b0a-8cbb-9ec558fc5f4e" />



<img width="1099" alt="Screenshot 2025-06-01 at 20 28 15" src="https://github.com/user-attachments/assets/f21ceb75-c132-4a8f-aaa2-1fbbc21e2d5f" />
