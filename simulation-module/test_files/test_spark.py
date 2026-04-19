from pyspark.sql import SparkSession

# Create Spark session (runs locally)
spark = SparkSession.builder \
    .appName("TestSetup") \
    .master("local[*]") \
    .getOrCreate()

print("✅ Spark session created!")
print(f"Spark version: {spark.version}")
print(f"Available cores: {spark.sparkContext.defaultParallelism}")

spark.stop()