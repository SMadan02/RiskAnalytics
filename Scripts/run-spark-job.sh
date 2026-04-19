#!/bin/bash

echo "Starting Risk Engine Streaming Job..."

# Use winpty on Windows to avoid path translation
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    winpty docker exec -it spark-master //opt//spark//bin//spark-submit \
      --master spark://spark-master:7077 \
      --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
      //opt//spark//work-dir//risk_engine_stream.py
else
    docker exec -it spark-master /opt/spark/bin/spark-submit \
      --master spark://spark-master:7077 \
      --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
      /opt/spark/work-dir/risk_engine_stream.py
fi