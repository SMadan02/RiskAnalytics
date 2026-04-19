"""
Configuration for Spark and Kafka connections
"""
# Lazy import: Only import Spark components when actually needed
# This allows the config to be imported in environments without Spark installed (e.g., Flask dashboard)
try:
    from pyspark.sql import SparkSession
    from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType
except ImportError:
    pass  # Spark not available in this environment

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = "kafka:29092"
KAFKA_TOPIC = "raw-market-data"

# Spark Configuration
SPARK_APP_NAME = "RiskEngineStreaming"
SPARK_MASTER = "spark://spark-master:7077"

# Database Configuration
DB_CONFIG = {
    "host": "timescaledb",
    "port": 5432,
    "database": "riskmetrics",
    "user": "riskengine",
    "password": "password123"
}

# Risk Calculation Parameters
RISK_PARAMS = {
    "mu": 0.0,
    "sigma": 0.30,
    "T": 1/252,
    "num_simulations": 10000,
    "confidence": 0.95
}


def create_spark_session(app_name: str = SPARK_APP_NAME):
    """Create and return configured SparkSession"""
    return SparkSession.builder \
        .appName(app_name) \
        .master(SPARK_MASTER) \
        .getOrCreate()


def get_market_data_schema():
    """Return schema for incoming market data"""
    return StructType([
        StructField("symbol", StringType(), True),
        StructField("price", DoubleType(), True),
        StructField("timestamp", StringType(), True),
        StructField("volume", LongType(), True)
    ])