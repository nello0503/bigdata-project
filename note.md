# Project Notes – Big Data Pipeline

Repository: https://github.com/nello0503/bigdata-project

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

## Issues Encountered

- Docker not available inside WSL: Docker Desktop was installed on Windows, but the `docker` command was not found in the Ubuntu distro. Fixed by enabling Settings → Resources → WSL Integration → Ubuntu in Docker Desktop.
- pandas 3 compatibility warning: running the Spark test printed a FutureWarning stating that PySpark does not yet fully support pandas >= 3.0.0. Fixed by downgrading with `pip install "pandas<3"` and updating requirements.txt.
- Docker Desktop must be running on Windows before using `docker` from the Ubuntu terminal, since the Docker engine runs in a separate WSL instance (docker-desktop) shared with the Ubuntu distro.
- Docker Desktop startup timeout (`HCS_E_CONNECTION_TIMEOUT`): the internal docker-desktop WSL instance did not respond. Fixed by running `wsl --shutdown`, updating WSL with `wsl --update` and restarting the PC.

## Dataset

- **Name:** Ist-Daten (actual data) – Swiss public transport
- **Publisher:** Open Data Mobility Switzerland (opentransportdata.swiss)
- **Dataset page:** https://opendata.swiss/en/perma/istdaten@oevch
- **File used:** 2026-10-31_istdaten.csv
- **Download URL:** https://data.opentransportdata.swiss/dataset/2091d9b2-8012-4d70-bf90-214ee6a9b458/resource/9f155590-7ca9-4e18-b292-f658fea49015/download/2026-10-31_istdaten.csv
- **License:** open use, source must be cited
- **Format:** CSV, `;` separator, UTF-8
- **Size:** 522 MB, 2,139,969 rows (one day of service), 22 columns

One file is published per day and contains every stop of every journey operated on that day (trains, buses, trams…), with scheduled and actual/forecast arrival and departure times. Daily files are only kept online for a limited period; older days are available in the historical archive.

### Main columns

| Column | Meaning |
|---|---|
| BETRIEBSTAG | Operating day |
| FAHRT_BEZEICHNER | Unique journey ID |
| BETREIBER_ABK / BETREIBER_NAME | Operator (e.g. SBB, DB) |
| PRODUKT_ID | Transport mode (Zug = train, Bus, Tram…) |
| LINIEN_TEXT / VERKEHRSMITTEL_TEXT | Line and service category (IC, IR, RE, S…) |
| ZUSATZFAHRT_TF | Extra journey not in timetable |
| FAELLT_AUS_TF | Journey cancelled |
| BPUIC / HALTESTELLEN_NAME | Stop code and name |
| ANKUNFTSZEIT / AN_PROGNOSE | Scheduled vs actual/forecast arrival |
| ABFAHRTSZEIT / AB_PROGNOSE | Scheduled vs actual/forecast departure |
| AN_PROGNOSE_STATUS / AB_PROGNOSE_STATUS | Quality of the actual time (REAL, PROGNOSE…) |
| DURCHFAHRT_TF | Pass-through without stopping |

Delay is computed as `AN_PROGNOSE - ANKUNFTSZEIT` (arrival) and `AB_PROGNOSE - ABFAHRTSZEIT` (departure).

### Data quality observations (first inspection)

- Separator is `;`, not `,`.
- Two timestamp formats: scheduled times as `dd.MM.yyyy HH:mm`, actual times as `dd.MM.yyyy HH:mm:ss`.
- Empty fields are expected: no arrival at the first stop, no departure at the last stop.
- Not all times are measured: the status columns distinguish real measurements (REAL) from forecasts (PROGNOSE). Delay analysis must state which statuses are included.
- Foreign stops are present (e.g. DB trains in Germany): a filter on Swiss stops may be needed.

## Analysis Questions

Definitions used throughout:
- Delay = actual/forecast time - scheduled time (AN_PROGNOSE - ANKUNFTSZEIT).
- Punctuality = share of arrivals with delay < 3 minutes (SBB definition).
- Journeys are counted as distinct FAHRT_BEZEICHNER, not as rows (one row = one journey at one stop).

1. **For each transport mode, which stops have the highest average arrival delay?**
   Top 5 stops per mode (train, bus, tram…), considering only stops with at least 50 arrivals, to exclude isolated cases.
   Columns: PRODUKT_ID, HALTESTELLEN_NAME, ANKUNFTSZEIT, AN_PROGNOSE.

2. **Which operator runs the most journeys, and are larger operators also more punctual?**
   For each operator: number of distinct journeys, average arrival delay and share of cancelled journeys.
   Columns: BETREIBER_ABK, FAHRT_BEZEICHNER, delay, FAELLT_AUS_TF.

3. **Which canton has the best punctuality score?**
   Punctuality per canton, with average delay and number of arrivals reported alongside. Requires a join with the official service points list (BPUIC -> municipality, canton). Rail services only; cantons below a minimum number of arrivals are excluded.

4. **How does punctuality change during the day?**
   Punctuality per hour of scheduled arrival, to compare peak hours (7-9, 17-19) with off-peak hours. Rail services only.
   Columns: ANKUNFTSZEIT (hour), delay.

5. **Does delay accumulate along a journey?**
   For each train journey, compares the delay at the first and at the last stop (stops ordered by scheduled time), and aggregates the difference by service category (IC, IR, RE, S…).
   Columns: FAHRT_BEZEICHNER, VERKEHRSMITTEL_TEXT, ANKUNFTSZEIT, ABFAHRTSZEIT, delay.

Scope decisions: see "Data Exploration" below.

## Data Exploration

Script: `src/explore.py` (PySpark, local mode). Full output: `docs/exploration_output.txt`.
Execution time on one daily file (522 MB): ~17 s.

### Volumes (one day, 2026-10-31)

| Metric | Value |
|---|---|
| Rows | 2,139,969 |
| Distinct journeys | 124,850 |
| Distinct stops | 40,808 |
| Operators | 137 |

One day already contains over 2 million rows: one year would be roughly 780 million rows, which justifies a distributed processing engine.

### Findings

- **Transport modes:** buses 80.4%, trams 10.8%, trains 8.0% (171,018 rows), plus metro, rack railway and boats.
- **Inconsistent values:** the same mode appears as `Bus` and `BUS` (12,352 rows), so PRODUKT_ID must be normalized before grouping.
- **Time status (train arrivals):** REAL 79.3%, NULL 8.2%, UNBEKANNT (unknown) 6.7%, PROGNOSE 5.7%. NULL status matches rows with no scheduled arrival (first stop of a journey, 14,847 rows), so it is expected. Among rows with an arrival time, about 87% are measured (REAL).
- **Country of the stop (trains):** Switzerland (UIC code 85) 91.8%; the rest are stops in Germany (80), Austria (81), France (87) and Italy (83), served by cross-border trains (ICE, TGV, TER, RB…).
- **Service categories (trains):** S 60.8%, R 20.0%, RE 6.2%, IR 5.3%, IC 2.0%, followed by foreign categories.
- **Flags (train rows):** 5,611 cancelled, 1,352 extra journeys, 118 pass-through. These are rows, not journeys: cancellation rates must be computed on distinct journeys.
- **Missing values (trains):** AN_PROGNOSE is empty in 26,293 rows vs 14,847 for ANKUNFTSZEIT: the difference corresponds to cancelled stops and stops without a reliable actual time.

### Scope decisions

1. **Delays are computed only on measured times** (status REAL); PROGNOSE and UNBEKANNT are excluded, losing about 13% of train arrivals in exchange for reliable values.
2. **Only Swiss stops** (BPUIC starting with 85) are analysed; foreign stops are kept in the raw zone.
3. **Cancelled journeys are excluded from delay statistics** and analysed separately as a cancellation rate.
4. **PRODUKT_ID is normalized to upper case** before any aggregation.
