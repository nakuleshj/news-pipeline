# Real-Time News NLP Pipeline on AWS

## Architecture
![alt text](https://github.com/nakuleshj/news-pipeline/blob/main/news-pipeline%20(2).png)

This serverless pipeline ingests news headlines via News API every 12 hours, stores raw JSON in S3, performs NLP-based sentiment enrichment using Lambda, writes Parquet to S3, and registers the schema in Glue Catalog. Trino (on EC2 Free Tier) queries the enriched data via the catalog to generate materialized business-ready views, which power an interactive Streamlit dashboard for analytics.
