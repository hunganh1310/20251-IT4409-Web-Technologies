"""
Real-time stream processing module.
Reads air quality data from Kafka and writes to TimescaleDB.
"""
import json
from datetime import datetime
from typing import Optional

import psycopg2
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, from_json, get_json_object
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, 
    DoubleType, TimestampType
)

from src.common import logger, settings


def get_spark_session() -> SparkSession:
    """Create and return a Spark session configured for Kafka streaming."""
    spark = SparkSession.builder \
        .appName("AirQuality-Realtime-Streaming") \
        .master("local[*]") \
        .config("spark.jars.packages", 
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,"
            "org.postgresql:postgresql:42.6.0") \
        .config("spark.sql.streaming.checkpointLocation", settings.spark_checkpoint_location) \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    return spark


def create_timescaledb_table(city: str) -> None:
    """Create TimescaleDB table for the city if it doesn't exist."""
    table_name = f"{city}_measurements"
    
    conn = psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password
    )
    
    try:
        with conn.cursor() as cur:
            # Create extension if not exists
            cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
            
            # Create table
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                measurement_time TIMESTAMPTZ NOT NULL,
                city VARCHAR(50) NOT NULL,
                aqi INTEGER,
                pm25 DOUBLE PRECISION,
                pm10 DOUBLE PRECISION,
                o3 DOUBLE PRECISION,
                no2 DOUBLE PRECISION,
                so2 DOUBLE PRECISION,
                co DOUBLE PRECISION,
                temperature DOUBLE PRECISION,
                humidity DOUBLE PRECISION,
                wind DOUBLE PRECISION,
                pressure DOUBLE PRECISION,
                PRIMARY KEY (measurement_time, city)
            );
            """
            cur.execute(create_table_sql)
            
            # Convert to hypertable (TimescaleDB)
            try:
                cur.execute(f"""
                    SELECT create_hypertable('{table_name}', 'measurement_time', 
                        if_not_exists => TRUE);
                """)
            except Exception as e:
                logger.warning(f"Hypertable may already exist: {e}")
            
            conn.commit()
            logger.info(f"Table {table_name} created/verified successfully")
    finally:
        conn.close()


def read_from_kafka(spark: SparkSession, city: str) -> DataFrame:
    """Read streaming data from Kafka topic."""
    topic = f"{settings.aqicn_topic}.{city}"
    
    kafka_options = {
        "kafka.bootstrap.servers": settings.kafka_bootstrap_servers,
        "subscribe": topic,
        "startingOffsets": "earliest",
        "failOnDataLoss": "false"
    }

    # Add SASL authentication if not using PLAINTEXT
    if settings.kafka_security_protocol != "PLAINTEXT":
        kafka_options["kafka.security.protocol"] = settings.kafka_security_protocol
        kafka_options["kafka.sasl.mechanism"] = settings.kafka_sasl_mechanism
        kafka_options["kafka.sasl.jaas.config"] = (
            f'org.apache.kafka.common.security.plain.PlainLoginModule required '
            f'username="{settings.kafka_sasl_username}" '
            f'password="{settings.kafka_sasl_password}";'
        )

    df = spark.readStream \
        .format("kafka") \
        .options(**kafka_options) \
        .load()

    return df


def parse_kafka_message(df: DataFrame) -> DataFrame:
    """Parse the Kafka message value and extract air quality data."""
    # Define schema for the payload
    payload_schema = StructType([
        StructField("aqi", IntegerType(), True),
        StructField("idx", IntegerType(), True),
        StructField("time", StructType([
            StructField("s", StringType(), True),
            StructField("tz", StringType(), True),
            StructField("v", IntegerType(), True),
            StructField("iso", StringType(), True)
        ]), True),
        StructField("iaqi", StructType([
            StructField("pm25", StructType([StructField("v", DoubleType(), True)]), True),
            StructField("pm10", StructType([StructField("v", DoubleType(), True)]), True),
            StructField("o3", StructType([StructField("v", DoubleType(), True)]), True),
            StructField("no2", StructType([StructField("v", DoubleType(), True)]), True),
            StructField("so2", StructType([StructField("v", DoubleType(), True)]), True),
            StructField("co", StructType([StructField("v", DoubleType(), True)]), True),
            StructField("t", StructType([StructField("v", DoubleType(), True)]), True),
            StructField("h", StructType([StructField("v", DoubleType(), True)]), True),
            StructField("w", StructType([StructField("v", DoubleType(), True)]), True),
            StructField("p", StructType([StructField("v", DoubleType(), True)]), True)
        ]), True)
    ])

    # Parse the JSON value
    df_parsed = df.select(
        col("value").cast("string").alias("raw_json"),
        col("timestamp").alias("kafka_timestamp")
    )
    
    # Extract city and payload from the message
    df_extracted = df_parsed.select(
        get_json_object(col("raw_json"), "$.city").alias("city"),
        get_json_object(col("raw_json"), "$.payload").alias("payload_json"),
        col("kafka_timestamp")
    )
    
    # Parse the payload
    df_with_payload = df_extracted.select(
        col("city"),
        from_json(col("payload_json"), payload_schema).alias("payload"),
        col("kafka_timestamp")
    )
    
    # Flatten the structure
    df_flat = df_with_payload.select(
        col("kafka_timestamp").alias("measurement_time"),
        col("city"),
        col("payload.aqi").alias("aqi"),
        col("payload.iaqi.pm25.v").alias("pm25"),
        col("payload.iaqi.pm10.v").alias("pm10"),
        col("payload.iaqi.o3.v").alias("o3"),
        col("payload.iaqi.no2.v").alias("no2"),
        col("payload.iaqi.so2.v").alias("so2"),
        col("payload.iaqi.co.v").alias("co"),
        col("payload.iaqi.t.v").alias("temperature"),
        col("payload.iaqi.h.v").alias("humidity"),
        col("payload.iaqi.w.v").alias("wind"),
        col("payload.iaqi.p.v").alias("pressure")
    )
    
    return df_flat


def write_batch_to_timescaledb(batch_df: DataFrame, batch_id: int, city: str) -> None:
    """Write a batch of data to TimescaleDB."""
    if batch_df.isEmpty():
        logger.info(f"Batch {batch_id} is empty, skipping")
        return
    
    table_name = f"{city}_measurements"
    rows = batch_df.collect()
    
    conn = psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password
    )
    
    try:
        with conn.cursor() as cur:
            for row in rows:
                insert_sql = f"""
                INSERT INTO {table_name} (
                    measurement_time, city, aqi, pm25, pm10, o3, no2, so2, co,
                    temperature, humidity, wind, pressure
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (measurement_time, city) DO UPDATE SET
                    aqi = EXCLUDED.aqi,
                    pm25 = EXCLUDED.pm25,
                    pm10 = EXCLUDED.pm10,
                    o3 = EXCLUDED.o3,
                    no2 = EXCLUDED.no2,
                    so2 = EXCLUDED.so2,
                    co = EXCLUDED.co,
                    temperature = EXCLUDED.temperature,
                    humidity = EXCLUDED.humidity,
                    wind = EXCLUDED.wind,
                    pressure = EXCLUDED.pressure;
                """
                cur.execute(insert_sql, (
                    row['measurement_time'],
                    row['city'],
                    row['aqi'],
                    row['pm25'],
                    row['pm10'],
                    row['o3'],
                    row['no2'],
                    row['so2'],
                    row['co'],
                    row['temperature'],
                    row['humidity'],
                    row['wind'],
                    row['pressure']
                ))
            conn.commit()
            logger.info(f"Batch {batch_id}: Inserted {len(rows)} records to {table_name}")
    except Exception as e:
        logger.error(f"Error writing batch {batch_id} to TimescaleDB: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def write_to_timescaledb(df: DataFrame, city: str):
    """Write streaming data to TimescaleDB."""
    def write_batch(batch_df: DataFrame, batch_id: int):
        write_batch_to_timescaledb(batch_df, batch_id, city)

    query = df.writeStream \
        .outputMode("append") \
        .foreachBatch(write_batch) \
        .option("checkpointLocation", f"{settings.spark_checkpoint_location}/realtime_{city}") \
        .trigger(processingTime="30 seconds") \
        .start()

    return query


def main(city: str) -> None:
    """Main entry point for real-time streaming processing."""
    logger.info(f"Starting real-time streaming for {city.upper()}")
    
    # Create table if not exists
    create_timescaledb_table(city)
    
    # Initialize Spark
    spark = get_spark_session()
    
    try:
        # Read from Kafka
        df_kafka = read_from_kafka(spark, city)
        
        # Parse messages
        df_parsed = parse_kafka_message(df_kafka)
        
        # Write to TimescaleDB
        query = write_to_timescaledb(df_parsed, city)
        
        logger.info(f"Real-time streaming started for {city.upper()}")
        query.awaitTermination()
        
    except KeyboardInterrupt:
        logger.info(f"Stopping real-time streaming for {city}")
    except Exception as e:
        logger.error(f"Error in real-time streaming for {city}: {e}")
        raise
    finally:
        spark.stop()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        city_arg = sys.argv[1]
    else:
        city_arg = "hanoi"
    main(city_arg)
