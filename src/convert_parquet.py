"""Convert the raw CSV to Parquet and compare size and query time."""
import glob
import os
import time
import statistics
from pyspark.sql import SparkSession, functions as F

CSV = "data/raw/*_istdaten.csv"
PARQUET = "data/parquet/istdaten"

spark = (SparkSession.builder.appName("convert_parquet")
         .config("spark.driver.memory", "4g")
         .getOrCreate())
spark.sparkContext.setLogLevel("ERROR")


def size_mb(path):
    """Size in MB of a file, a set of files given with a '*' pattern, or a directory."""
    matches = glob.glob(path)
    if matches and all(os.path.isfile(f) for f in matches):
        return sum(os.path.getsize(f) for f in matches) / 1024**2
    return sum(os.path.getsize(os.path.join(root, f))
               for root, _, files in os.walk(path) for f in files) / 1024**2


# 1. Conversion: same content, columnar format, partitioned by operating day
t0 = time.time()
df = spark.read.csv(CSV, sep=";", header=True)
df = df.withColumn("operating_day", F.to_date("BETRIEBSTAG", "dd.MM.yyyy"))
df.write.mode("overwrite").partitionBy("operating_day").parquet(PARQUET)
conversion_time = time.time() - t0

parquet_files = [f for _, _, fs in os.walk(PARQUET) for f in fs if f.endswith(".parquet")]

# 2. Benchmark: same queries on CSV and on Parquet
readers = {
    "CSV": lambda: spark.read.csv(CSV, sep=";", header=True),
    "Parquet": lambda: spark.read.parquet(PARQUET),
}
queries = {
    "count all rows": lambda d: d.count(),
    "trains per category (2 columns)": lambda d: d.filter(F.col("PRODUKT_ID") == "Zug")
                                                  .groupBy("VERKEHRSMITTEL_TEXT").count().collect(),
}


def bench(read, query, runs=3):
    query(read())  # warm-up run, not measured
    times = []
    for _ in range(runs):
        t = time.time()
        query(read())
        times.append(time.time() - t)
    return statistics.median(times)


csv_mb, pq_mb = size_mb(CSV), size_mb(PARQUET)
print("\n=== Storage ===")
print(f"CSV:     {csv_mb:8.1f} MB ({len(glob.glob(CSV))} files)")
print(f"Parquet: {pq_mb:8.1f} MB ({len(parquet_files)} files)")
print(f"Reduction: {100 * (1 - pq_mb / csv_mb):.1f}%")
print(f"Conversion time: {conversion_time:.1f} s")

print("\n=== Query time (median of 3 runs, seconds) ===")
print(f"{'Query':35} {'CSV':>8} {'Parquet':>8} {'Speed-up':>9}")
for name, q in queries.items():
    t_csv = bench(readers["CSV"], q)
    t_pq = bench(readers["Parquet"], q)
    print(f"{name:35} {t_csv:8.2f} {t_pq:8.2f} {t_csv / t_pq:8.1f}x")

spark.stop()
