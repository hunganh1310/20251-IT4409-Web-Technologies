from pyspark.sql import SparkSession

# Khởi tạo Spark Session
spark = SparkSession \
    .builder \
    .appName("KafkaReader") \
    .getOrCreate()

# Đọc dữ liệu từ Kafka topic 'test-topic'
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "my-kafka-cluster-kafka-bootstrap:9092") \
    .option("subscribe", "test-topic") \
    .load()

# Chuyển đổi dữ liệu nhận được thành dạng chuỗi và in ra màn hình
query = df.selectExpr("CAST(value AS STRING)") \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()