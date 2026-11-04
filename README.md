# Big Data Pipeline

Exam project for **Algorithms and Data Structures for Big Data** (Università Niccolò Cusano).

End-to-end data pipeline covering ingestion, processing, storage and analytics, built with Apache Spark and Docker.

## Dataset

**Ist-Daten (actual data)** – Swiss public transport, published daily by Open Data Mobility Switzerland.
Each file contains every stop of every journey operated on one day, with scheduled and actual arrival/departure times, used to analyse delays and cancellations.

- **Dataset page:** https://data.opentransportdata.swiss/dataset/ist-daten-v2
- **File used:** `2026-10-31_istdaten.csv` (~522 MB, CSV with `;` separator)
- **License:** Open use, must provide the source

Download the file into the raw zone:
```bash
wget -P data/raw "https://data.opentransportdata.swiss/dataset/2091d9b2-8012-4d70-bf90-214ee6a9b458/resource/9f155590-7ca9-4e18-b292-f658fea49015/download/2026-10-31_istdaten.csv"
```

Daily files are kept online only for a limited period; older days are available in the historical archive on opentransportdata.swiss.

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
