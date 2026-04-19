"""
Real-time risk calculation streaming job
"""
from pyspark.sql.types import StructType, StructField, DoubleType
from pyspark.sql.functions import from_json, col, window, last, lit, udf, current_timestamp, to_timestamp
import psycopg2

# Import from package
from risk_package.config import (
    create_spark_session, 
    get_market_data_schema,
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC,
    DB_CONFIG,
    RISK_PARAMS
)
from risk_package.monte_carlo_spark import run_monte_carlo_var

# Create Spark session
spark = create_spark_session()

# Schema for incoming data
market_data_schema = get_market_data_schema()

# Read from Kafka
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

# Parse JSON and convert timestamp
parsed_df = raw_df.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), market_data_schema).alias("data")) \
    .select("data.*") \
    .withColumn("timestamp", to_timestamp(col("timestamp")))

# Aggregate to get latest price per symbol
latest_price_df = parsed_df \
    .withWatermark("timestamp", "1 minute") \
    .groupBy("symbol", window("timestamp", "30 seconds")) \
    .agg(last("price").alias("current_price"))

# Define UDF return schema
risk_schema = StructType([
    StructField("var_95", DoubleType(), True),
    StructField("es_95", DoubleType(), True)
])

# Register UDF
@udf(returnType=risk_schema)
def calculate_risk_udf(price):
    """Calculate VaR and ES using Monte Carlo simulation"""
    var, es = run_monte_carlo_var(
        current_price=float(price),
        **RISK_PARAMS
    )
    return (float(var), float(es))

# Apply UDF
risk_df = latest_price_df.withColumn("risk", calculate_risk_udf(col("current_price"))) \
    .select(
        col("symbol"),
        col("current_price"),
        col("risk.var_95").alias("var_95"),
        col("risk.es_95").alias("es_95"),
        lit(RISK_PARAMS["num_simulations"]).alias("num_simulations"),
        current_timestamp().alias("calculation_time")
    )

# Database writer
def write_to_db(batch_df, batch_id):
    """Write each micro-batch to PostgreSQL"""
    pandas_df = batch_df.toPandas()
    
    if len(pandas_df) == 0:
        print(f"Batch {batch_id}: No data to write")
        return
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    for _, row in pandas_df.iterrows():
        cursor.execute("""
            INSERT INTO risk_metrics (timestamp, symbol, current_price, var_95, es_95, num_simulations)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            row['calculation_time'],
            row['symbol'],
            row['current_price'],
            row['var_95'],
            row['es_95'],
            row['num_simulations']
        ))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Batch {batch_id}: Wrote {len(pandas_df)} records to database")

# Start streaming query
query = risk_df.writeStream \
    .outputMode("update") \
    .foreachBatch(write_to_db) \
    .option("checkpointLocation", "/tmp/spark_checkpoints/risk_engine") \
    .trigger(processingTime="30 seconds") \
    .start()

query.awaitTermination()