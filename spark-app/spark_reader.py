from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, broadcast, expr
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType, IntegerType

# --- Định nghĩa Schema ---
sensor_schema = StructType([
    StructField("location_id", StringType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("pm25", DoubleType(), True),
    StructField("pm10", DoubleType(), True),
])

location_schema = StructType([
    StructField("loc_id", StringType(), True),
    StructField("latitude", DoubleType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("sensor_model", StringType(), True),
])

weather_schema = StructType([
    StructField("weather_location_id", StringType(), True),
    StructField("weather_time", TimestampType(), True),
    StructField("temperature", DoubleType(), True),
    StructField("humidity", DoubleType(), True),
    StructField("wind_speed", DoubleType(), True),
])

# --- Khởi tạo Spark Session ---
spark = SparkSession \
    .builder \
    .appName("KafkaAirQualityJoins") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
print("--- Spark Session đã khởi tạo ---")

# --- Đọc luồng dữ liệu cảm biến từ Kafka ---
print("--- Bắt đầu đọc luồng dữ liệu cảm biến từ Kafka ---")
raw_sensor_stream = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "test-topic") \
    .option("startingOffsets", "latest") \
    .load()

parsed_sensor_stream = raw_sensor_stream \
    .select(from_json(col("value").cast("string"), sensor_schema).alias("data")) \
    .select("data.*") \
    .withColumnRenamed("location_id", "sensor_location_id")

print("--- Đã đọc và parse luồng cảm biến ---")

# --- Stream-Static Join (Dữ liệu cảm biến + Metadata vị trí) ---
print("--- Thực hiện Stream-Static Join với metadata vị trí ---")
location_metadata_df = spark.read \
    .csv("/app/locations.csv", header=True, schema=location_schema)

enriched_static_stream = parsed_sensor_stream.join(
    broadcast(location_metadata_df),
    parsed_sensor_stream.sensor_location_id == location_metadata_df.loc_id,
    "left"
)

print("--- Đã hoàn thành Stream-Static Join ---")

# --- Stream-Stream Join (Dữ liệu cảm biến đã làm giàu + Thời tiết) ---
print("--- Bắt đầu đọc luồng dữ liệu thời tiết từ Kafka ---")
raw_weather_stream = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "weather-raw") \
    .option("startingOffsets", "latest") \
    .load()

parsed_weather_stream = raw_weather_stream \
    .select(from_json(col("value").cast("string"), weather_schema).alias("data")) \
    .select("data.*")

print("--- Đã đọc và parse luồng thời tiết ---")

# --- Đặt Watermarks ---
print("--- Đặt Watermarks ---")
sensor_stream_with_watermark = enriched_static_stream \
    .withWatermark("timestamp", "10 minutes")

weather_stream_with_watermark = parsed_weather_stream \
    .withWatermark("weather_time", "15 minutes")

# --- Thực hiện Stream-Stream Join ---
print("--- Thực hiện Stream-Stream Join ---")
final_enriched_stream = sensor_stream_with_watermark.join(
    weather_stream_with_watermark,
    expr("""
        sensor_location_id = weather_location_id AND
        timestamp >= weather_time - interval 5 minutes AND
        timestamp <= weather_time + interval 5 minutes
    """),
    "leftOuter"
)

print("--- Đã hoàn thành Stream-Stream Join ---")

# --- Ghi kết quả ra Console ---
print("--- Bắt đầu ghi kết quả ra Console ---")
query = final_enriched_stream \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .start()

print("--- Chờ stream kết thúc ---")
query.awaitTermination()
