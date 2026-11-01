# Big Data Pipeline

Exam project for **Algorithms and Data Structures for Big Data** (Università Niccolò Cusano).

End-to-end data pipeline covering ingestion, processing, storage and analytics, built with Apache Spark and Docker.

## Dataset
_To be defined._ The source link will be reported here to make the experiments reproducible.

## Architecture
_To be defined._

## Requirements
- Linux or Windows with WSL2
- Java 17
- Python 3 with `venv`
- Docker and Docker Compose

## Setup
```bash
git clone https://github.com/nello0503/bigdata-project.git
cd bigdata-project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Check that Spark works:
```bash
python src/test_spark.py
```

## Project structure
```
data/raw/          downloaded data (not versioned)
data/processed/    processed data in Parquet format
src/               ingestion, processing and query scripts
notebooks/         exploration and experiments
docs/              report and architecture diagrams
```

## Author
Aniello Matrisciano
