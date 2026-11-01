from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("test").getOrCreate()
df = spark.createDataFrame([(1, "a"), (2, "b"), (3, "c")], ["id", "lettera"])
df.show()
df.write.mode("overwrite").parquet("data/processed/test")
print("Spark e Parquet funzionano")
spark.stop()
