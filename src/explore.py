"""First exploration of the Ist-Daten file: volumes, transport modes, data quality."""
import time
from pyspark.sql import SparkSession, functions as F

PATH = "data/raw/2026-10-31_istdaten.csv"

spark = (SparkSession.builder.appName("explore")
         .config("spark.driver.memory", "4g")
         .getOrCreate())
spark.sparkContext.setLogLevel("ERROR")
t0 = time.time()

# Read the CSV: ';' separator, first row = column names
df = spark.read.csv(PATH, sep=";", header=True)

# Country = first 2 digits of the stop code (85 = Switzerland, 80 = Germany, 83 = Italy...)
df = df.withColumn("COUNTRY", F.substring("BPUIC", 1, 2)).cache()

total = df.count()

def section(title):
    print(f"\n=== {title} ===")

def with_pct(d, base):
    return d.withColumn("pct", F.round(100 * F.col("count") / base, 2)).orderBy(F.desc("count"))

section("Volumes")
print(f"Rows:              {total:,}")
print(f"Distinct journeys: {df.select('FAHRT_BEZEICHNER').distinct().count():,}")
print(f"Distinct stops:    {df.select('BPUIC').distinct().count():,}")
print(f"Operators:         {df.select('BETREIBER_ABK').distinct().count():,}")

section("Rows by transport mode")
with_pct(df.groupBy("PRODUKT_ID").count(), total).show(truncate=False)

# From here on: trains only
trains = df.filter(F.col("PRODUKT_ID") == "Zug")
n_trains = trains.count()

section("Train arrivals by time status (REAL = measured, PROGNOSE = forecast)")
with_pct(trains.groupBy("AN_PROGNOSE_STATUS").count(), n_trains).show(truncate=False)

section("Train rows by country of the stop")
with_pct(trains.groupBy("COUNTRY").count(), n_trains).show(truncate=False)

section("Train service categories")
with_pct(trains.groupBy("VERKEHRSMITTEL_TEXT").count(), n_trains).show(15, truncate=False)

section("Flags on train rows")
trains.select(
    F.sum(F.when(F.col("FAELLT_AUS_TF") == "true", 1).otherwise(0)).alias("cancelled"),
    F.sum(F.when(F.col("ZUSATZFAHRT_TF") == "true", 1).otherwise(0)).alias("extra_journey"),
    F.sum(F.when(F.col("DURCHFAHRT_TF") == "true", 1).otherwise(0)).alias("pass_through"),
).show()

section("Empty values in key train columns")
cols = ["ANKUNFTSZEIT", "AN_PROGNOSE", "ABFAHRTSZEIT", "AB_PROGNOSE", "HALTESTELLEN_NAME"]
trains.select([F.sum(F.col(c).isNull().cast("int")).alias(c) for c in cols]).show()

print(f"\nExecution time: {time.time() - t0:.1f} s")
spark.stop()
