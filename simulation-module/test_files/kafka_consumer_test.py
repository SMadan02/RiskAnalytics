from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType
from pyspark.sql.functions import from_json, col
from config import create_spark_session, KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, CHECKPOINT_LOCATION, PROCESSING_INTERVAL

# TODO: Create SparkSession
spark = create_spark_session()

# TODO: Define schema for MarketData
market_data_schema = StructType([
    StructField("symbol", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("timestamp", StringType(), True),  # ISO 8601 timestamp from producer
    StructField("volume", LongType(), True)
])
# Fields: symbol, price, timestamp, volume

# TODO: Read from Kafka
# what is bootstrap server? It's the address of the Kafka broker. In this case, it's "kafka:29092" because we're running Kafka in a Docker container and that's how we can access it from our Spark application.
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .load()  # Only read NEW messages

# TODO: Parse JSON
parsed_df = raw_df.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), market_data_schema).alias("data")) \
    .select("data.*")
# Cast value to string
# Use from_json() with schema
# Select fields

# TODO: Write to console
query = parsed_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .trigger(processingTime=PROCESSING_INTERVAL) \
    .start()
# Use writeStream
# outputMode("append")
# format("console")
# option("truncate", "false")
# trigger(processingTime="10 seconds")
# start()

# TODO: Keep running
query.awaitTermination()