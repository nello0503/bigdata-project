# Project Notes – Big Data Pipeline

## Development Environment

The project is developed on Windows through WSL2 (Windows Subsystem for Linux) running Ubuntu, on a PC with 16 GB of RAM. WSL2 runs a real Linux kernel: it avoids the known Spark/Hadoop compatibility issues on native Windows and reproduces the Linux environment typical of Big Data clusters. Compared to a traditional virtual machine, it allocates memory dynamically, leaving more resources available to Spark and to the containers.

| Component | Version | Role |
|---|---|---|
| Ubuntu (WSL2) | 26.04 | Linux environment |
| Java (OpenJDK) | 17.0.20.1 | Runtime required by Spark (JVM) |
| Python | 3.14.4 | Scripting language |
| PySpark | 4.3.0 | Distributed processing engine |
| pandas | 2.3.3 | Data exploration (< 3 for PySpark compatibility) |
| pyarrow | 26.0.0 | Parquet read/write |
| Docker | 29.9.2 | Service containerization |
| Docker Compose | 5.6.1 | Container orchestration |
| Git / GitHub | 2.53.0 | Version control |

## Design Rationale

- Docker: each service (storage, Spark, database) runs in a container with a pinned version, so the whole pipeline starts with a single command on any machine. This meets the reproducibility requirement.
- Spark: processes data in memory and in parallel; the same code runs locally and on a cluster, so the solution is ready to scale even if the current dataset is small.
- Python virtual environment + requirements.txt: pins library versions so that different runs produce the same results.
- pandas < 3: PySpark does not yet fully support pandas 3, so the version is pinned to avoid incompatibilities.
- Data excluded from the repository: datasets are not versioned because of their size; they are re-downloaded by the ingestion script from the original source, which is cited in the report.

## Repository Structure

~~~
bigdata-project/
├── data/raw/          downloaded data, never modified (data lake raw zone)
├── data/processed/    processed data in Parquet format
├── src/               ingestion, processing and query scripts
├── notebooks/         exploration and experiments
├── docs/              report and architecture diagrams
├── note.md            notes on design choices and rationale
└── requirements.txt   Python dependencies with pinned versions
~~~

## Environment Check

Tested with src/test_spark.py: creating a Spark DataFrame and writing it to Parquet completed successfully. Warnings about the loopback address and the native-hadoop library are expected in a local WSL environment and do not affect functionality.

## Dataset
(to be completed)

## Analysis Questions
(to be completed)
