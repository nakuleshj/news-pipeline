import json
import os
from datetime import date, datetime, timedelta

import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from dotenv import load_dotenv
from minio import Minio, S3Error

load_dotenv()


NEWS_API_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

FETCH_INTERVAL_HOURS = 12

MINIO_CLIENT= Minio(
    endpoint="minio:9000",
    access_key="minioadmin",
    secret_key="admin123",
    secure=False,
)

BUCKET = "bronze"

if not MINIO_CLIENT.bucket_exists(BUCKET):
    MINIO_CLIENT.make_bucket(BUCKET)

def fetch_news():
    params = {
        "apiKey": NEWS_API_KEY,
        "from": datetime.now() - timedelta(hours=FETCH_INTERVAL_HOURS),
        "to": datetime.now(),
        "sortBy": "publishedAt",
    }
    try:
        response = requests.get(NEWS_API_ENDPOINT, params=params)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        return {}

def upload_data_minio():
    data=fetch_news()
    today = datetime.now()
    filename = f"{today.hour}.json"
    object_path = f"{today.year}/{today.month}/{today.day}/{filename}"

    with open(filename, "w") as f:
        json.dump(data, f)

    try:
        MINIO_CLIENT.fput_object(
            bucket_name=BUCKET,
            object_name=object_path,
            file_path=filename,
            content_type="application/json",
        )
        print(f"Uploaded {object_path} to bucket '{BUCKET}'")
    except S3Error as e:
        print(f"Upload error: {e}")
    finally:
        os.remove(filename)

with DAG(
    dag_id="news_ingest",
    start_date=datetime(2024, 1, 1, 9),
    schedule=timedelta(hours=FETCH_INTERVAL_HOURS),
    catchup=False,
) as dag:
    ingest_raw_news = PythonOperator(
        task_id="ingest_raw_news",
        python_callable=upload_data_minio,
    )
    ingest_raw_news