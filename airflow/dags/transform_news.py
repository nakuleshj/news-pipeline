import json
import os
from datetime import date, datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from dotenv import load_dotenv
from minio import Minio, S3Error

load_dotenv()

MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

MINIO_CLIENT= Minio(
    endpoint="minio:9000",
    access_key= MINIO_ACCESS_KEY,
    secret_key= MINIO_SECRET_KEY,
    secure=False,
)

BRONZE_BUCKET = "bronze"

SILVER_BUCKET= "silver"

with DAG(
    dag_id="news_ingest",
    start_date=datetime(2024, 1, 1, 9),
    catchup=False,
) as dag:
    transform_news = PythonOperator(
        task_id="transform_news",
        python_callable=transform_news,
    )
    transform_news
